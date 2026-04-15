# Troubleshooting

## 1. `pio` Command Not Found

Cause: PlatformIO not installed or not in PATH.

Fix:

```bash
python3 -m pip install --user platformio
python3 -m platformio --version
```

Use `python3 -m platformio` if `pio` is still unavailable.

## 2. Sender Shows `sender_send` Fail

Cause: wrong receiver MAC, channel mismatch, or receiver not running.

Fix:

1. Monitor receiver and copy fresh `receiver_ready.receiverMac`.
2. Update sender `kReceiverMac`.
3. Reflash sender.

## 3. No Dashboard Telemetry

Checks:

1. Browser supports Web Serial (Chrome/Edge/Brave).
2. Open via `http://localhost` or HTTPS.
3. Correct serial port selected.
4. Receiver monitor shows telemetry lines.

## 4. pH Looks Wrong

Symptoms:

- pH stuck too low/high
- `pH ADC` near 0 or 4095

Fix:

1. Verify analog pH output wiring and shared ground.
2. Use RAW voltage for calibration (`docs/CALIBRATION_GUIDE.md`).
3. Avoid clipped points when fitting constants.

## 5. Packet Version/Size Errors

Cause: sender and receiver built from different protocol versions.

Fix:

1. Flash receiver first.
2. Flash sender second.
3. Confirm both report packet version 2.

## 6. Receiver Drops Packets

Symptom: `receiver_queue_full` errors or rising `dropped` stats.

Fix:

1. Ensure serial consumer (dashboard/monitor) is connected and responsive.
2. Reduce extra serial noise.
3. Keep only one active monitor on the same serial port.

## 7. Malformed JSON Lines In Dashboard Log

Cause: normal startup serial noise during boot/sync.

Fix:

1. Wait a few seconds after connect.
2. Ignore occasional startup malformed-line entries unless persistent.
