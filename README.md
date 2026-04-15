# Water Telemetry Monorepo

ESP32 sender/receiver telemetry system for water-quality style sensors.
The sender publishes sensor data over ESP-NOW, the receiver bridges it to USB serial NDJSON, and the web dashboard visualizes both processed metrics and RAW diagnostics.

## Prerequisites

You must install PlatformIO before any `pio ...` command will work.

1. Python 3.9+ installed.
2. PlatformIO Core installed and available in PATH.
3. Chrome/Edge/Brave for Web Serial dashboard.

Quick install example:

```bash
python3 -m pip install --user platformio
python3 -m platformio --version
```

If `pio` is not found after install, use `python3 -m platformio` or add the user scripts path to PATH.

Detailed setup: `docs/SETUP_GUIDE.md`

## Repository Structure

- `esp-sender/`: Sender firmware (real sensor read + calibration)
- `esp-receiver/`: Receiver firmware (ESP-NOW -> NDJSON bridge)
- `web/`: Browser dashboard (Web Serial)
- `docs/`: Setup, flashing, calibration, troubleshooting, backend roadmap

## Current Protocol (v2)

- Packet version: `2`
- Sender interval: `2000 ms`
- Shared packed payload includes processed values and RAW diagnostics.
- Receiver emits `type=telemetry` and periodic `type=receiver_stats` JSON lines.

## Quick Start

1. Flash receiver first:

```bash
cd /sub-mission/esp-receiver
pio run -t upload
pio device monitor -b 115200
```

Expected startup message:

```json
{"type":"receiver_ready","packetVersion":2,"receiverMac":"..","baud":115200}
```

2. Copy receiver MAC into sender `kReceiverMac` in `esp-sender/src/main.cpp`, then flash sender:

```bash
cd /sub-mission/esp-sender
pio run -t upload
pio device monitor -b 115200
```

3. Run dashboard:

```bash
cd /sub-mission/web
python3 -m http.server 8080
```

Open `http://localhost:8080` and click Connect Serial.

Detailed flash workflow: `docs/FLASHING_GUIDE.md`

## Calibration And Diagnostics

- pH is calibrated from RAW voltage in sender firmware.
- Dashboard shows RAW ADC/voltage fields for all analog sensors.
- Use RAW values as calibration reference before trusting processed values.

Calibration guide: `docs/CALIBRATION_GUIDE.md`

Troubleshooting guide: `docs/TROUBLESHOOTING.md`

## Notes

1. Sender and receiver firmware versions must match (coordinated update).
2. Receiver should be flashed before sender when protocol changes.
3. Backend/API roadmap remains in `docs/BACKEND_ROADMAP.md`.
