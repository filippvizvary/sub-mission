#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <math.h>

namespace {

constexpr uint32_t kBaudRate = 115200;
constexpr uint8_t kPacketVersion = 2;
constexpr uint8_t kEspNowChannel = 1;
constexpr size_t kQueueSize = 16;
constexpr uint32_t kStatsIntervalMs = 5000;

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

// Keep receiver and sender packet layouts byte-for-byte identical.
static_assert(sizeof(TelemetryPacket) == 61,
              "TelemetryPacket size mismatch between receiver and sender");

struct ReceivedFrame {
  TelemetryPacket packet;
  uint8_t mac[6];
  int32_t rssi;
  uint32_t receivedMs;
  bool hasRssi;
};

ReceivedFrame g_queue[kQueueSize];
size_t g_head = 0;
size_t g_tail = 0;
size_t g_count = 0;

uint32_t g_totalPackets = 0;
uint32_t g_validPackets = 0;
uint32_t g_invalidPackets = 0;
uint32_t g_droppedPackets = 0;
uint32_t g_sequenceGaps = 0;
uint32_t g_lastSequence = 0;
bool g_hasSequence = false;
uint32_t g_lastStatsMs = 0;
uint32_t g_lastValidPacketMs = 0;
uint32_t g_recentValidPackets = 0;

// The ESP-NOW receive callback runs in the WiFi task, not the Arduino loop.
// It must not touch Serial: printing from there interleaves with a telemetry
// line and corrupts the NDJSON. Record the fault and let loop() emit it.
enum : uint8_t {
  kDeferredErrorNone = 0,
  kDeferredErrorNullPointers,
  kDeferredErrorSizeMismatch,
  kDeferredErrorVersionMismatch,
  kDeferredErrorQueueFull,
};
volatile uint8_t g_deferredError = kDeferredErrorNone;
volatile int32_t g_deferredErrorA = 0;
volatile int32_t g_deferredErrorB = 0;

portMUX_TYPE g_queueMux = portMUX_INITIALIZER_UNLOCKED;

void macToString(const uint8_t *mac, char *out, size_t outSize) {
  snprintf(out, outSize, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2],
           mac[3], mac[4], mac[5]);
}

void enqueueFrame(const ReceivedFrame &frame) {
  portENTER_CRITICAL(&g_queueMux);
  if (g_count >= kQueueSize) {
    g_droppedPackets++;
    portEXIT_CRITICAL(&g_queueMux);
    g_deferredErrorA = static_cast<int32_t>(g_droppedPackets);
    g_deferredError = kDeferredErrorQueueFull;
    return;
  }

  g_queue[g_tail] = frame;
  g_tail = (g_tail + 1) % kQueueSize;
  g_count++;
  portEXIT_CRITICAL(&g_queueMux);
}

bool dequeueFrame(ReceivedFrame &frame) {
  portENTER_CRITICAL(&g_queueMux);
  if (g_count == 0) {
    portEXIT_CRITICAL(&g_queueMux);
    return false;
  }

  frame = g_queue[g_head];
  g_head = (g_head + 1) % kQueueSize;
  g_count--;
  portEXIT_CRITICAL(&g_queueMux);
  return true;
}

// JSON has no NaN or Infinity. A railed sender channel arrives as NAN in the
// packet, so serialise it as null. A raw %.3f of NAN would print the token
// "nan", which is invalid JSON and makes the dashboard drop the whole line.
void formatJsonFloat(char *out, size_t outSize, float value) {
  if (isfinite(value)) {
    snprintf(out, outSize, "%.3f", value);
  } else {
    snprintf(out, outSize, "null");
  }
}

void emitTelemetryJson(const ReceivedFrame &frame) {
  char macString[18] = {0};
  macToString(frame.mac, macString, sizeof(macString));

  char temperature[16];
  char ph[16];
  char flow[16];
  char turbidity[16];
  char tds[16];
  char rssi[16];
  formatJsonFloat(temperature, sizeof(temperature), frame.packet.temperature);
  formatJsonFloat(ph, sizeof(ph), frame.packet.ph);
  formatJsonFloat(flow, sizeof(flow), frame.packet.flow);
  formatJsonFloat(turbidity, sizeof(turbidity), frame.packet.turbidity);
  formatJsonFloat(tds, sizeof(tds), frame.packet.tds);
  if (frame.hasRssi) {
    snprintf(rssi, sizeof(rssi), "%ld", static_cast<long>(frame.rssi));
  } else {
    snprintf(rssi, sizeof(rssi), "null");
  }

  // One buffer, one write. Multiple Serial.print calls would let a concurrent
  // writer land in the middle of the line and invalidate the JSON.
  char line[640];
  snprintf(line, sizeof(line),
           "{\"type\":\"telemetry\",\"version\":%u,\"mac\":\"%s\",\"sequence\":%lu,"
           "\"temperature\":%s,\"ph\":%s,\"flow\":%s,\"turbidity\":%s,\"tds\":%s,"
           "\"senderUptimeMs\":%lu,\"receiverUptimeMs\":%lu,\"rssi\":%s,"
           "\"raw\":{\"tempAdc\":%u,\"phAdc\":%u,\"tdsAdc\":%u,\"turbidityAdc\":%u,"
           "\"tempVoltage\":%.3f,\"phVoltage\":%.3f,\"tdsVoltage\":%.3f,"
           "\"turbidityVoltage\":%.3f,\"flowPulseCount\":%lu,\"flowWindowMs\":%lu}}",
           frame.packet.version, macString,
           static_cast<unsigned long>(frame.packet.sequence),
           temperature, ph, flow, turbidity, tds,
           static_cast<unsigned long>(frame.packet.senderUptimeMs),
           static_cast<unsigned long>(frame.receivedMs), rssi,
           static_cast<unsigned int>(frame.packet.tempAdc),
           static_cast<unsigned int>(frame.packet.phAdc),
           static_cast<unsigned int>(frame.packet.tdsAdc),
           static_cast<unsigned int>(frame.packet.turbidityAdc),
           frame.packet.tempVoltage, frame.packet.phVoltage, frame.packet.tdsVoltage,
           frame.packet.turbidityVoltage,
           static_cast<unsigned long>(frame.packet.flowPulseCount),
           static_cast<unsigned long>(frame.packet.flowWindowMs));
  Serial.println(line);
}

void emitStatsJson() {
  const bool hasValid = g_validPackets > 0;
  const uint32_t lastPacketAgeMs = hasValid ? (millis() - g_lastValidPacketMs) : 0;

  Serial.printf(
      "{\"type\":\"receiver_stats\",\"total\":%lu,\"valid\":%lu,\"invalid\":%lu,"
      "\"dropped\":%lu,\"sequenceGaps\":%lu,\"queueDepth\":%u,\"uptimeMs\":%lu,"
      "\"recentValid\":%lu,\"lastPacketAgeMs\":",
      static_cast<unsigned long>(g_totalPackets),
      static_cast<unsigned long>(g_validPackets),
      static_cast<unsigned long>(g_invalidPackets),
      static_cast<unsigned long>(g_droppedPackets),
      static_cast<unsigned long>(g_sequenceGaps), static_cast<unsigned int>(g_count),
      static_cast<unsigned long>(millis()),
      static_cast<unsigned long>(g_recentValidPackets));

  if (hasValid) {
    Serial.printf("%lu", static_cast<unsigned long>(lastPacketAgeMs));
  } else {
    Serial.print("null");
  }

  Serial.println("}");
  g_recentValidPackets = 0;
}

void onDataReceived(const uint8_t *macAddress, const uint8_t *incomingData, int len) {
  g_totalPackets++;

  if (macAddress == nullptr || incomingData == nullptr) {
    g_invalidPackets++;
    g_deferredError = kDeferredErrorNullPointers;
    return;
  }

  if (len != static_cast<int>(sizeof(TelemetryPacket))) {
    g_invalidPackets++;
    g_deferredErrorA = static_cast<int32_t>(sizeof(TelemetryPacket));
    g_deferredErrorB = len;
    g_deferredError = kDeferredErrorSizeMismatch;
    return;
  }

  TelemetryPacket packet;
  memcpy(&packet, incomingData, sizeof(packet));

  if (packet.version != kPacketVersion) {
    g_invalidPackets++;
    g_deferredErrorA = static_cast<int32_t>(kPacketVersion);
    g_deferredErrorB = static_cast<int32_t>(packet.version);
    g_deferredError = kDeferredErrorVersionMismatch;
    return;
  }

  if (g_hasSequence && packet.sequence > g_lastSequence + 1) {
    g_sequenceGaps += (packet.sequence - (g_lastSequence + 1));
  }
  g_lastSequence = packet.sequence;
  g_hasSequence = true;

  ReceivedFrame frame{};
  frame.packet = packet;
  memcpy(frame.mac, macAddress, sizeof(frame.mac));
  frame.receivedMs = millis();
  frame.hasRssi = false;
  frame.rssi = 0;

  g_validPackets++;
  g_recentValidPackets++;
  g_lastValidPacketMs = frame.receivedMs;
  enqueueFrame(frame);
}

void startEspNowReceiver() {
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_wifi_set_channel(kEspNowChannel, WIFI_SECOND_CHAN_NONE) != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_wifi_set_channel_failed\"}");
    return;
  }

  if (esp_now_init() != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_now_init_failed\"}");
    return;
  }

  esp_now_register_recv_cb(onDataReceived);

  char receiverMac[18] = {0};
  uint8_t mac[6] = {0};
  WiFi.macAddress(mac);
  macToString(mac, receiverMac, sizeof(receiverMac));

  Serial.printf(
      "{\"type\":\"receiver_ready\",\"packetVersion\":%u,\"receiverMac\":\"%s\","
      "\"baud\":%lu}\n",
      kPacketVersion, receiverMac, static_cast<unsigned long>(kBaudRate));
}

}  // namespace

void setup() {
  Serial.begin(kBaudRate);

  uint32_t waitStart = millis();
  while (!Serial && (millis() - waitStart) < 1500) {
    delay(10);
  }

  startEspNowReceiver();
  g_lastStatsMs = millis();
}

void loop() {
  // All Serial output happens here, in one context.
  if (g_deferredError != kDeferredErrorNone) {
    const uint8_t code = g_deferredError;
    g_deferredError = kDeferredErrorNone;
    switch (code) {
      case kDeferredErrorQueueFull:
        Serial.printf("{\"type\":\"error\",\"message\":\"receiver_queue_full\",\"dropped\":%ld}\n",
                      static_cast<long>(g_deferredErrorA));
        break;
      case kDeferredErrorSizeMismatch:
        Serial.printf("{\"type\":\"error\",\"message\":\"packet_size_mismatch\",\"expected\":%ld,\"received\":%ld}\n",
                      static_cast<long>(g_deferredErrorA), static_cast<long>(g_deferredErrorB));
        break;
      case kDeferredErrorVersionMismatch:
        Serial.printf("{\"type\":\"error\",\"message\":\"packet_version_mismatch\",\"expected\":%ld,\"received\":%ld}\n",
                      static_cast<long>(g_deferredErrorA), static_cast<long>(g_deferredErrorB));
        break;
      default:
        Serial.println("{\"type\":\"error\",\"message\":\"packet_invalid_null_pointers\"}");
        break;
    }
  }

  ReceivedFrame frame;
  while (dequeueFrame(frame)) {
    emitTelemetryJson(frame);
  }

  const uint32_t now = millis();
  if (now - g_lastStatsMs >= kStatsIntervalMs) {
    emitStatsJson();
    g_lastStatsMs = now;
  }

  delay(10);
}