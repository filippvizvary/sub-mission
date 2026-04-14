# CODE Documentation

## 1. Project Overview

This workspace contains two ESP32 PlatformIO projects intended to work as a telemetry link:

- Receiver project: `/home/filip/submission/esp-receiver`
- Sender project: `/home/filip/submission/esp-sender`

Target system behavior:

1. Sender ESP32 reads sensor values (temperature, pH, flow, turbidity, TDS).
2. Sender transmits telemetry frames over ESP-NOW.
3. Receiver ESP32 listens for ESP-NOW frames.
4. Receiver emits parsed telemetry as NDJSON over USB serial.
5. Local browser dashboard reads serial via Web Serial and displays live telemetry.

Current implementation status:

- Receiver firmware: implemented.
- Receiver web dashboard: implemented.
- Sender firmware: implemented with random-value telemetry simulation.

---

## 2. Workspace Structure

### 2.1 Receiver (`esp-receiver`)

- `platformio.ini`
  - ESP32 Arduino environment (`esp32dev`)
  - Serial monitor speed set to `115200`
- `src/main.cpp`
  - Full ESP-NOW receiver and NDJSON serial bridge
- `README.md`
  - Setup, payload, and run instructions

### 2.2 Workspace Web (`web`)

- `index.html`
  - Dashboard markup
- `app.js`
  - Web Serial connection + stream parser + UI updates
- `styles.css`
  - Dashboard styling and responsive layout

### 2.3 Sender (`esp-sender`)

- `platformio.ini`
  - ESP32 Arduino project config with serial monitor at `115200`
- `src/main.cpp`
  - ESP-NOW sender with periodic random telemetry generation

---

## 3. Receiver Firmware Design (`esp-receiver/src/main.cpp`)

### 3.1 Core constants

- `kBaudRate = 115200`
  - USB serial speed used by firmware and dashboard.
- `kPacketVersion = 1`
  - Protocol version gate for payload compatibility.
- `kQueueSize = 16`
  - Internal ring buffer depth between callback context and loop processing.
- `kStatsIntervalMs = 5000`
  - Periodic stats emission interval.

### 3.2 Data structures

#### `TelemetryPacket` (packed)

Represents raw ESP-NOW payload bytes:

- `uint8_t version`
- `uint32_t sequence`
- `float temperature`
- `float ph`
- `float flow`
- `float turbidity`
- `float tds`
- `uint32_t senderUptimeMs`

#### `ReceivedFrame`

Internal enriched frame used before serial output:

- `TelemetryPacket packet`
- `uint8_t mac[6]`
- `int32_t rssi`
- `uint32_t receivedMs`
- `bool hasRssi`

Note: current callback API variant in this project does not provide RSSI metadata, so `hasRssi` is `false` and `rssi` is output as `null`.

### 3.3 Concurrency and buffering model

- ESP-NOW callback (`onDataReceived`) runs when packets arrive.
- Callback validates and copies payload into a fixed-size ring queue.
- Main `loop()` drains queue and prints NDJSON lines.
- Queue operations are protected by `portMUX_TYPE` critical sections.

Why this design:

- Keeps callback short and deterministic.
- Avoids doing heavy serial formatting in interrupt-adjacent context.
- Adds drop visibility through `g_droppedPackets` when queue overflows.

### 3.4 Receiver lifecycle

#### `setup()`

1. Starts serial at 115200.
2. Waits briefly for serial attach (up to ~1.5s).
3. Calls `startEspNowReceiver()`.
4. Initializes stats timer.

#### `startEspNowReceiver()`

1. Sets Wi-Fi mode to `WIFI_STA`.
2. Calls `WiFi.disconnect()`.
3. Initializes ESP-NOW with `esp_now_init()`.
4. Registers receive callback with `esp_now_register_recv_cb(onDataReceived)`.
5. Gets receiver MAC address and emits `receiver_ready` JSON line.

Error path:

- If `esp_now_init()` fails, emits:
  - `{"type":"error","message":"esp_now_init_failed"}`

### 3.5 Packet receive path

#### `onDataReceived(const uint8_t* macAddress, const uint8_t* incomingData, int len)`

Processing sequence:

1. Increments `g_totalPackets`.
2. Validates null pointers and exact payload size.
3. Copies bytes into `TelemetryPacket`.
4. Validates `packet.version == kPacketVersion`.
5. Detects sequence gaps and updates `g_sequenceGaps`.
6. Builds `ReceivedFrame` with source MAC and receiver timestamp.
7. Enqueues frame.
8. Updates valid/invalid counters.

### 3.6 Serial output path

#### Telemetry emission

`emitTelemetryJson()` prints one NDJSON object with fields:

- `type: telemetry`
- `version`
- `mac`
- `sequence`
- `temperature`
- `ph`
- `flow`
- `turbidity`
- `tds`
- `senderUptimeMs`
- `receiverUptimeMs`
- `rssi` (currently `null`)

#### Stats emission

`emitStatsJson()` periodically prints:

- `type: receiver_stats`
- `total`
- `valid`
- `invalid`
- `dropped`
- `sequenceGaps`
- `queueDepth`
- `uptimeMs`

### 3.7 Main loop behavior

`loop()` repeatedly:

1. Dequeues all pending frames and emits telemetry JSON per frame.
2. Emits stats every 5 seconds.
3. Delays for 10 ms.

---

## 4. Receiver Protocol Contract

### 4.1 Binary payload contract (sender -> receiver)

Sender must transmit exactly the packed `TelemetryPacket` byte layout and set:

- `version = 1`

Any payload with mismatched size or version is rejected and counted as invalid.

### 4.2 Serial contract (receiver -> dashboard)

- Transport: USB serial
- Baud: 115200
- Encoding: UTF-8 text JSON
- Framing: NDJSON (one complete JSON object per line)

Consumers must parse line-by-line and tolerate occasional malformed/non-telemetry lines.

---

## 5. Dashboard Design (`web`)

### 5.1 UI composition (`index.html`)

Main sections:

- Hero text
- Control panel
  - Connect Serial button
  - Disconnect button
  - Status pill
- Metadata cards
  - Sender MAC
  - Sequence
  - RSSI
  - Updated timestamp
- Metric cards
  - Temperature
  - pH
  - Flow
  - Turbidity
  - TDS
- Log panel

### 5.2 Frontend logic (`app.js`)

State variables:

- `port`, `reader`
- `keepReading`
- `textBuffer` for partial line accumulation

Main functions:

- `connectSerial()`
  - Requests serial port from browser.
  - Opens at 115200.
  - Pipes stream through `TextDecoderStream`.
  - Starts read loop and updates UI state.
- `readLoop()`
  - Reads text chunks.
  - Splits by newline.
  - Preserves incomplete tail in `textBuffer`.
  - Passes complete lines to `processLine()`.
- `processLine()`
  - JSON parses each line.
  - Routes by `payload.type`.
  - Handles malformed JSON by logging and continuing.
- `updateTelemetry()`
  - Updates all metric and metadata fields.
- `disconnectSerial()`
  - Cancels reader, releases lock, closes port, updates UI.

Supported message types:

- `telemetry`
- `receiver_ready`
- `receiver_stats`
- `error`

### 5.3 Styling (`styles.css`)

- Responsive card-grid layout.
- Distinct status color states:
  - idle
  - connected
  - error
- Gradient/radial background and modern typography.
- Mobile adjustments for status layout.

---

## 6. Current Sender Project Status (`esp-sender`)

The sender project is implemented and currently provides telemetry simulation:

- Initializes ESP-NOW and configures a fixed receiver peer.
- Sends protocol-compatible `TelemetryPacket` frames every 1000 ms.
- Generates random test values for temperature, pH, flow, turbidity, and TDS.
- Maintains and increments packet sequence numbers.
- Emits sender status logs (`sender_ready`, `sender_packet`, `sender_send`).

It is ready for phase-2 sensor integration.

---

## 7. Build and Run Guide

### 7.1 Receiver firmware

From receiver project directory:

1. Build: `pio run`
2. Upload: `pio run -t upload`
3. Monitor: `pio device monitor -b 115200`

Note: in this terminal environment, the `pio` command may be unavailable even if PlatformIO extension works inside VS Code.

### 7.2 Dashboard

Run local server from the workspace web folder:

- `cd /home/filip/submission/web`
- `python3 -m http.server 8080`

Open `http://localhost:8080` in a Chromium-based browser (Chrome/Edge/Brave), then connect serial.

---

## 8. Data and Reliability Notes

- Queue overflow is tracked via `dropped` counter.
- Sequence continuity is tracked via `sequenceGaps`.
- Invalid packets (wrong size/version) are tracked via `invalid`.
- Telemetry formatting precision is 3 decimals in firmware output.
- Dashboard display precision is currently 2 decimals.

---

## 9. Known Limitations

1. Sender currently uses simulated values (real sensor drivers pending).
2. Receiver currently accepts all senders (no MAC whitelist).
3. RSSI is unavailable in current callback signature and emitted as `null`.
4. Dashboard requires Web Serial support, so Chromium-based browsers are required.
5. No persistent storage/history yet (live view only).

---

## 10. Recommended Next Implementation Steps

1. Integrate real sensor inputs in sender firmware while keeping protocol compatibility.
2. Add configurable receiver peer filtering (optional whitelist mode).
3. Add sender/receiver health counters and long-run stability soak tests.
4. Add persistent backend logging with collector service and database.
5. Add historical charts from API data (not only live Web Serial).
6. Add end-to-end protocol regression tests and documentation versioning.

---

## 11. Quick Technical Summary

The implemented system core is a reliable receiver-side bridge:

- ESP-NOW binary telemetry in
- validation + buffering + counters
- NDJSON stream out over serial
- browser-based live visualization over Web Serial

This gives a stable integration target for the upcoming sender implementation and sensor wiring phase.
This gives a stable baseline for phase-2 sensor integration and backend persistence.
