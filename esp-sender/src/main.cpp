#include <Arduino.h>
#include <WiFi.h>
#include <esp_now.h>
#include <esp_system.h>
#include <esp_wifi.h>

namespace {

constexpr uint32_t kBaudRate = 115200;
constexpr uint8_t kPacketVersion = 1;
constexpr uint32_t kSendIntervalMs = 1000;
constexpr uint8_t kEspNowChannel = 1;

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
};

uint32_t g_sequence = 0;
uint32_t g_lastSendMs = 0;

float randomFloat(float minValue, float maxValue) {
  const float unit = static_cast<float>(esp_random()) /
                     static_cast<float>(UINT32_MAX);
  return minValue + unit * (maxValue - minValue);
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

  esp_now_peer_info_t peerInfo{};
  memcpy(peerInfo.peer_addr, kReceiverMac, sizeof(kReceiverMac));
  peerInfo.channel = kEspNowChannel;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("{\"type\":\"error\",\"message\":\"esp_now_add_peer_failed\"}");
    return false;
  }

  return true;
}

TelemetryPacket buildRandomPacket() {
  TelemetryPacket packet{};
  packet.version = kPacketVersion;
  packet.sequence = ++g_sequence;
  packet.temperature = randomFloat(20.0f, 32.0f);
  packet.ph = randomFloat(6.2f, 8.4f);
  packet.flow = randomFloat(0.0f, 12.0f);
  packet.turbidity = randomFloat(1.0f, 180.0f);
  packet.tds = randomFloat(120.0f, 900.0f);
  packet.senderUptimeMs = millis();
  return packet;
}

void sendTelemetry() {
  const TelemetryPacket packet = buildRandomPacket();
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
      "{\"type\":\"sender_packet\",\"sequence\":%lu,\"temperature\":%.3f,\"ph\":%.3f,\"flow\":%.3f,\"turbidity\":%.3f,\"tds\":%.3f}\n",
      static_cast<unsigned long>(packet.sequence), packet.temperature, packet.ph,
      packet.flow, packet.turbidity, packet.tds);
}

}  // namespace

void setup() {
  Serial.begin(kBaudRate);

  uint32_t waitStart = millis();
  while (!Serial && (millis() - waitStart) < 1500) {
    delay(10);
  }

  randomSeed(esp_random());

  if (!initEspNowSender()) {
    return;
  }

  Serial.println("{\"type\":\"sender_ready\",\"packetVersion\":1,\"intervalMs\":1000}");
}

void loop() {
  const uint32_t now = millis();
  if (now - g_lastSendMs >= kSendIntervalMs) {
    sendTelemetry();
    g_lastSendMs = now;
  }

  delay(5);
}