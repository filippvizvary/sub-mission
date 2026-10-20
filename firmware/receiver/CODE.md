# CODE Documentation

This document describes the current receiver-side implementation and protocol expectations.

## 1. Current Project State

- Sender firmware: implemented with real sensor reads and pH calibration.
- Receiver firmware: implemented as ESP-NOW to serial NDJSON bridge.
- Web dashboard: implemented with processed metrics and RAW diagnostics fields.

## 2. Protocol Version

- Active packet version: `2`
- Sender and receiver must use the exact same packed `TelemetryPacket` layout.
- Firmware should be updated in a coordinated manner (receiver first, sender second).

## 3. Receiver Responsibilities

1. Start Wi-Fi in STA mode and initialize ESP-NOW.
2. Receive binary telemetry packets from sender.
3. Validate packet size and version.
4. Queue valid packets in a ring buffer.
5. Emit NDJSON telemetry and periodic receiver stats over USB serial.

## 4. Packet Shape (v2)

`TelemetryPacket` includes:

- `version`
- `sequence`
- `temperature`
- `ph`
- `flow`
- `turbidity`
- `tds`
- `senderUptimeMs`
- RAW fields:
  - `tempAdc`, `phAdc`, `tdsAdc`, `turbidityAdc`
  - `tempVoltage`, `phVoltage`, `tdsVoltage`, `turbidityVoltage`
  - `flowPulseCount`, `flowWindowMs`

## 5. Serial Output Contract

Receiver emits line-delimited JSON (`NDJSON`) at `115200` baud.

Main message types:

- `type=receiver_ready`
- `type=telemetry`
- `type=receiver_stats`
- `type=error`

`telemetry` includes both processed fields and a `raw` object for diagnostics.

## 6. Queueing Model

- Fixed ring buffer (`kQueueSize`) decouples ESP-NOW callback from serial printing.
- Overflow increments dropped counter and emits queue-full error.
- Queue operations are protected by critical sections.

## 7. Operational Notes

1. Receiver currently does not enforce sender MAC allowlist.
2. RSSI is currently emitted as `null`.
3. Sequence-gap logic assumes a single sender stream.
4. Packet mismatch (size/version) increments invalid counter and emits error logs.

## 8. Related Guides

- Root quick start and prerequisites: `README.md`
- Environment setup: `docs/SETUP_GUIDE.md`
- Flashing workflow: `docs/FLASHING_GUIDE.md`
- Calibration workflow: `docs/CALIBRATION_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
