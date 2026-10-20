# Setup Guide

This guide prepares a fresh machine to build and flash this project.

## 1. Install Requirements

1. Install Python 3.9+.
2. Install PlatformIO Core.
3. Verify `pio` works before continuing.

```bash
python3 -m pip install --user platformio
python3 -m platformio --version
```

If `pio` is not found:

1. Use `python3 -m platformio` instead of `pio`.
2. Add your Python user scripts directory to PATH.

## 2. Optional VS Code Extension

If you use VS Code, install the PlatformIO IDE extension for easier upload/monitor tasks.

## 3. Hardware/USB Checks

1. Connect each ESP32 by USB.
2. Confirm serial ports are visible:

```bash
pio device list
```

3. If no device appears, check cable/driver/power.

## 4. Verify Project Builds

```bash
cd /home/filip/sub-mission/esp-receiver
pio run

cd /home/filip/sub-mission/esp-sender
pio run
```

Build must pass before flashing.

## 5. Next Step

Proceed to `docs/FLASHING_GUIDE.md`.
