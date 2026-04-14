# Water Telemetry Monorepo

End-to-end ESP32 telemetry system for water-quality style metrics using ESP-NOW, with a local browser dashboard over Web Serial.

## Current Architecture

Data flow:

1. `esp-sender` (ESP32) generates random telemetry values every 1000 ms.
2. Sender transmits a packed `TelemetryPacket` over ESP-NOW (channel 1).
3. `esp-receiver` (ESP32) receives packets, validates them, and emits NDJSON over USB serial (115200 baud).
4. `web` dashboard reads serial with Web Serial API and renders live values.

## Repository Structure

- `esp-sender/`: Sender firmware (simulated telemetry)
- `esp-receiver/`: Receiver firmware (ESP-NOW -> NDJSON bridge)
- `web/`: Browser dashboard (Web Serial)
- `docs/`: Architecture and backend roadmap

## Protocol Contract

Sender and receiver share this packed payload:

- `uint8_t version`
- `uint32_t sequence`
- `float temperature`
- `float ph`
- `float flow`
- `float turbidity`
- `float tds`
- `uint32_t senderUptimeMs`

Notes:

- `version` must be `1`
- Sender currently transmits every `1000 ms`
- Receiver emits JSON lines with `type=telemetry` and periodic `type=receiver_stats`

## Quick Start

### 1. Flash Receiver

```bash
cd /submission/esp-receiver
pio run -t upload
pio device monitor -b 115200
```

Expected startup line includes receiver MAC:

```json
{"type":"receiver_ready","packetVersion":1,"receiverMac":"..","baud":115200}
```

### 2. Flash Sender

Set receiver MAC in `esp-sender/src/main.cpp` (`kReceiverMac`) to match receiver startup output.

```bash
cd /submission/esp-sender
pio run -t upload
pio device monitor -b 115200
```

Expected sender logs include:

- `type=sender_ready`
- `type=sender_packet`
- `type=sender_send` with mostly `status=ok`

### 3. Run Dashboard

```bash
cd /submission/web
python3 -m http.server 8080
```

Open `http://localhost:8080` in Chrome/Edge/Brave and click Connect Serial.

## Current Stability Status

From current validation:

- Sender and receiver are communicating successfully.
- Receiver stats are increasing with `invalid=0`, `dropped=0`, `sequenceGaps=0` in healthy runs.
- Dashboard is receiving and rendering live values.

## Known Limitations

1. Sender uses simulated random values (real sensors not integrated yet).
2. Receiver currently accepts any sender MAC.
3. RSSI is currently `null` in telemetry output.
4. Web dashboard has no persistent history (live-only).
5. No backend/API/database yet.

## Stability Recommendations

1. Add sender retry/re-init logic if repeated send failures occur.
2. Add optional sender MAC allowlist on receiver.
3. Add stricter payload sanity checks before forwarding to dashboard.
4. Add health counters and alert thresholds (fail ratio, stale data, queue depth).
5. Add long-duration soak tests (12-24h) to validate sustained operation.

## Next Architecture (Server + Database)

Recommended production direction:

1. Run a local PC collector service reading receiver serial NDJSON.
2. Collector writes telemetry into a database (PostgreSQL recommended).
3. Expose REST/WebSocket API from backend service.
4. Dashboard reads from API instead of direct Web Serial.

Detailed plan: `docs/BACKEND_ROADMAP.md`
