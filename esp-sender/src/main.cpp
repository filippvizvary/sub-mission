#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <math.h>

namespace {

constexpr uint32_t kBaudRate = 115200;
constexpr uint8_t kPacketVersion = 2;
constexpr uint32_t kSendIntervalMs = 2000;
constexpr uint8_t kEspNowChannel = 1;

constexpr uint8_t kTempPin = 34;
constexpr uint8_t kPhPin = 35;
constexpr uint8_t kTdsPin = 32;
constexpr uint8_t kTurbidityPin = 33;
constexpr uint8_t kFlowPin = 27;

constexpr float kSeriesResistor = 10000.0f;
constexpr float kNominalResistance = 10000.0f;
constexpr float kNominalTempC = 25.0f;
constexpr float kBCoefficient = 3950.0f;
constexpr float kAdcMax = 4095.0f;
constexpr float kVcc = 3.3f;
// YF-style flow sensors are commonly calibrated as frequency / 6.5 ~= L/min.
constexpr float kFlowCalibrationFactor = 6.5f;
constexpr float kPhCalibrationSlope = -5.48f;
constexpr float kPhCalibrationOffset = 14.67f;
constexpr float kPhMin = 0.0f;
constexpr float kPhMax = 14.0f;
constexpr float kTdsMin = 0.0f;
constexpr float kTdsMax = 2000.0f;
constexpr float kTurbidityMin = 0.0f;
constexpr float kTurbidityMax = 3000.0f;

// Replace with the receiver MAC printed in receiver_ready.
constexpr uint8_t kReceiverMac[6] = {0xE4, 0x65, 0xB8, 0x7A, 0x7C, 0x68};

struct __attribute__((packed)) TelemetryPacket {
  uint8_t version;
  uint32_t sequence;
  float temperature;
  float ph;
  float flow;
  float turbidity;
  float tds;
  uint32_t senderUptimeMs;
  uint16_t tempAdc;
  uint16_t phAdc;
  uint16_t tdsAdc;
  uint16_t turbidityAdc;
  float tempVoltage;
  float phVoltage;
  float tdsVoltage;
  float turbidityVoltage;
  uint32_t flowPulseCount;
  uint32_t flowWindowMs;
};

// Keep sender and receiver packet layouts byte-for-byte identical.
static_assert(sizeof(TelemetryPacket) == 61,
              "TelemetryPacket size mismatch between sender and receiver");

struct AnalogReading {
  uint16_t adc;
  float voltage;
};

struct TemperatureReading {
  float celsius;
  AnalogReading raw;
};

struct PhReading {
  float ph;
  AnalogReading raw;
};

struct TdsReading {
  float ppm;
  AnalogReading raw;
};

struct TurbidityReading {
  float ntu;
  AnalogReading raw;
};

struct FlowReading {
  float litersPerMinute;
  uint32_t pulseCount;
  uint32_t windowMs;
};

struct SensorReadings {
  TemperatureReading temperature;
  PhReading ph;
  TdsReading tds;
  TurbidityReading turbidity;
  FlowReading flow;
};

uint32_t g_sequence = 0;
uint32_t g_lastSendMs = 0;
volatile uint32_t g_flowPulseCount = 0;
uint32_t g_lastFlowSampleMs = 0;
float g_flowRate = 0.0f;
uint32_t g_lastFlowWindowPulseCount = 0;
uint32_t g_lastFlowWindowMs = 0;

void IRAM_ATTR onFlowPulse() {
  g_flowPulseCount++;
}

AnalogReading readAnalogPin(uint8_t pin) {
  const uint16_t adc = static_cast<uint16_t>(analogRead(pin));
  const float voltage = static_cast<float>(adc) * kVcc / kAdcMax;
  return {adc, voltage};
}

TemperatureReading readTemperatureC() {
  const AnalogReading raw = readAnalogPin(kTempPin);
  const float voltage = raw.voltage;

  if (voltage <= 0.0f || voltage >= kVcc) {
    return {NAN, raw};
  }

  const float resistance = kSeriesResistor * (kVcc / voltage - 1.0f);
  float temp = resistance / kNominalResistance;
  temp = log(temp);
  temp /= kBCoefficient;
  temp += 1.0f / (kNominalTempC + 273.15f);
  temp = 1.0f / temp;
  return {temp - 273.15f, raw};
}

PhReading readPh() {
  const AnalogReading raw = readAnalogPin(kPhPin);
  const float calibratedPh =
      kPhCalibrationSlope * raw.voltage + kPhCalibrationOffset;
  const float clampedPh =
      calibratedPh < kPhMin ? kPhMin
                            : (calibratedPh > kPhMax ? kPhMax : calibratedPh);
  return {clampedPh, raw};
}

TdsReading readTds() {
  const AnalogReading raw = readAnalogPin(kTdsPin);
  const float voltage = raw.voltage;
  const float ppm =
      (133.42f * voltage * voltage * voltage - 255.86f * voltage * voltage +
       857.39f * voltage) *
      0.5f;
  const float clampedPpm = ppm < kTdsMin ? kTdsMin : (ppm > kTdsMax ? kTdsMax : ppm);
  return {clampedPpm, raw};
}

TurbidityReading readTurbidity() {
  const AnalogReading raw = readAnalogPin(kTurbidityPin);
  const float ntu =
      -1120.4f * raw.voltage * raw.voltage + 5742.3f * raw.voltage - 4352.9f;
  const float clampedNtu =
      ntu < kTurbidityMin ? kTurbidityMin
                          : (ntu > kTurbidityMax ? kTurbidityMax : ntu);
  return {clampedNtu, raw};
}

FlowReading updateAndReadFlowRate() {
  const uint32_t now = millis();
  if (g_lastFlowSampleMs == 0) {
    g_lastFlowSampleMs = now;
    return {g_flowRate, g_lastFlowWindowPulseCount, g_lastFlowWindowMs};
  }

  const uint32_t elapsed = now - g_lastFlowSampleMs;
  if (elapsed < kSendIntervalMs) {
    return {g_flowRate, g_lastFlowWindowPulseCount, g_lastFlowWindowMs};
  }

  noInterrupts();
  const uint32_t pulseCount = g_flowPulseCount;
  g_flowPulseCount = 0;
  interrupts();

  g_lastFlowWindowPulseCount = pulseCount;
  g_lastFlowWindowMs = elapsed;
  g_flowRate = ((1000.0f / static_cast<float>(elapsed)) *
                static_cast<float>(pulseCount)) /
               kFlowCalibrationFactor;
  g_lastFlowSampleMs = now;
  return {g_flowRate, g_lastFlowWindowPulseCount, g_lastFlowWindowMs};
}

void onDataSent(const uint8_t *macAddr, esp_now_send_status_t status) {
  if (macAddr == nullptr) {
    return;
  }

  Serial.printf(
      "{\"type\":\"sender_send\",\"sequence\":%lu,\"status\":\"%s\"}\n",
      static_cast<unsigned long>(g_sequence),
      status == ESP_NOW_SEND_SUCCESS ? "ok" : "fail");
}

bool initEspNowSender() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_wifi_set_channel(kEspNowChannel, WIFI_SECOND_CHAN_NONE) != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_wifi_set_channel_failed\"}");
    return false;
  }

  if (esp_now_init() != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_now_init_failed\"}");
    return false;
  }

  esp_now_register_send_cb(onDataSent);

  Serial.printf(
      "{\"type\":\"sender_peer_target\",\"receiverMac\":\"%02X:%02X:%02X:%02X:%02X:%02X\"}\n",
      kReceiverMac[0], kReceiverMac[1], kReceiverMac[2], kReceiverMac[3],
      kReceiverMac[4], kReceiverMac[5]);

  esp_now_peer_info_t peerInfo{};
  memcpy(peerInfo.peer_addr, kReceiverMac, sizeof(kReceiverMac));
  peerInfo.channel = kEspNowChannel;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_now_add_peer_failed\"}");
    return false;
  }

  Serial.println("{\"type\":\"sender_peer_added\",\"status\":\"ok\"}");

  return true;
}

SensorReadings readSensors() {
  SensorReadings readings{};
  readings.temperature = readTemperatureC();
  readings.ph = readPh();
  readings.flow = updateAndReadFlowRate();
  readings.turbidity = readTurbidity();
  readings.tds = readTds();

  if (!isfinite(readings.temperature.celsius)) {
    Serial.printf(
        "{\"type\":\"error\",\"message\":\"temperature_sensor_fault\",\"tempAdc\":%u,\"tempVoltage\":%.3f}\n",
        static_cast<unsigned int>(readings.temperature.raw.adc),
        readings.temperature.raw.voltage);
  }

  if (readings.ph.raw.adc == 0 || readings.ph.raw.adc >= static_cast<uint16_t>(kAdcMax)) {
    Serial.printf(
        "{\"type\":\"warn\",\"message\":\"ph_signal_rail\",\"phAdc\":%u,\"phVoltage\":%.3f}\n",
        static_cast<unsigned int>(readings.ph.raw.adc), readings.ph.raw.voltage);
  }

  return readings;
}

TelemetryPacket buildSensorPacket(const SensorReadings &readings) {
  TelemetryPacket packet{};
  packet.version = kPacketVersion;
  packet.sequence = ++g_sequence;
  packet.temperature = readings.temperature.celsius;
  packet.ph = readings.ph.ph;
  packet.flow = readings.flow.litersPerMinute;
  packet.turbidity = readings.turbidity.ntu;
  packet.tds = readings.tds.ppm;
  packet.senderUptimeMs = millis();
  packet.tempAdc = readings.temperature.raw.adc;
  packet.phAdc = readings.ph.raw.adc;
  packet.tdsAdc = readings.tds.raw.adc;
  packet.turbidityAdc = readings.turbidity.raw.adc;
  packet.tempVoltage = readings.temperature.raw.voltage;
  packet.phVoltage = readings.ph.raw.voltage;
  packet.tdsVoltage = readings.tds.raw.voltage;
  packet.turbidityVoltage = readings.turbidity.raw.voltage;
  packet.flowPulseCount = readings.flow.pulseCount;
  packet.flowWindowMs = readings.flow.windowMs;
  return packet;
}

void sendTelemetry() {
  const SensorReadings readings = readSensors();
  const TelemetryPacket packet = buildSensorPacket(readings);
  const esp_err_t sendResult =
      esp_now_send(kReceiverMac, reinterpret_cast<const uint8_t *>(&packet),
                   sizeof(packet));

  if (sendResult != ESP_OK) {
    Serial.printf(
        "{\"type\":\"error\",\"message\":\"esp_now_send_failed\",\"code\":%d}\n",
        static_cast<int>(sendResult));
    return;
  }

  Serial.printf(
      "{\"type\":\"sender_packet\",\"sequence\":%lu,\"temperature\":%.3f,\"ph\":%.3f,\"flow\":%.3f,\"turbidity\":%.3f,\"tds\":%.3f,\"ph_adc\":%u,\"ph_v\":%.3f}\n",
      static_cast<unsigned long>(packet.sequence), packet.temperature, packet.ph,
      packet.flow, packet.turbidity, packet.tds,
      static_cast<unsigned int>(packet.phAdc), packet.phVoltage);
}

}  // namespace

void setup() {
  Serial.begin(kBaudRate);

  uint32_t waitStart = millis();
  while (!Serial && (millis() - waitStart) < 1500) {
    delay(10);
  }

  pinMode(kFlowPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(kFlowPin), onFlowPulse, RISING);

  if (!initEspNowSender()) {
    return;
  }

  Serial.println("{\"type\":\"sender_ready\",\"packetVersion\":2,\"intervalMs\":2000}");
}

void loop() {
  const uint32_t now = millis();
  if (now - g_lastSendMs >= kSendIntervalMs) {
    sendTelemetry();
    g_lastSendMs = now;
  }

  delay(5);
}