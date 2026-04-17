# Architecture and Data Flow

This guide explains the full path from a physical sensor reading on the sender ESP32 to the final values shown in the browser dashboard on the PC.

It also explains ESP-NOW in plain terms, because that protocol is the core link between the two ESP32 boards.

## The Short Version

1. A sensor changes an electrical signal on the sender board.
2. The sender firmware reads that signal, converts it into engineering units, and packs both processed values and raw diagnostics into one binary packet.
3. The sender transmits that packet to the receiver over ESP-NOW.
4. The receiver validates the packet, adds metadata such as MAC address and receive time, and prints one JSON line to USB serial.
5. The PC browser dashboard reads those JSON lines over Web Serial and updates the live UI.

The current protocol version is `2`. Sender and receiver must use the exact same packed `TelemetryPacket` layout.

## System Overview

```text
Sensors on sender -> sender firmware -> ESP-NOW radio link -> receiver firmware
-> USB serial NDJSON -> browser dashboard -> live cards and RAW diagnostics
```

You can think of the receiver as a bridge. It does not do the sensor math itself. Its job is to accept wireless packets from the sender and turn them into a stable serial stream that the PC can consume.

## Step 1: Sensor Signal Enters The Sender

The sender board samples these inputs:

- Temperature on ADC pin `34`
- pH on ADC pin `35`
- TDS on ADC pin `32`
- Turbidity on ADC pin `33`
- Flow sensor pulses on GPIO `27`

The analog sensors are read as ADC counts and converted to voltage using the board ADC range. The flow sensor is counted as pulses over a sampling window.

The sender firmware then turns those raw electrical readings into the displayed measurements:

- Temperature in degrees Celsius
- pH in pH units
- Flow in liters per minute
- Turbidity in NTU
- TDS in ppm

The sender code for this lives in [esp-sender/src/main.cpp](../esp-sender/src/main.cpp).

## Step 2: Sender Builds One Packed Telemetry Packet

After reading the sensors, the sender creates one binary `TelemetryPacket`.

That packet contains two kinds of data:

- Processed values, such as temperature, pH, flow, turbidity, and TDS
- RAW diagnostics, such as ADC counts, voltages, flow pulse count, and flow window length

It also includes:

- `version` so the receiver can reject mismatched firmware
- `sequence` so packets can be tracked in order
- `senderUptimeMs` so the receiver and dashboard can know how long the sender has been running

The important design rule is that the sender and receiver structs must stay byte-for-byte identical. If the packet layout changes on one side and not the other, the receiver will reject the payload or decode garbage.

The sender sends the packet every `2000 ms`.

## Step 3: ESP-NOW Moves The Packet Wirelessly

ESP-NOW is a low-latency, connectionless protocol built on top of the ESP32 Wi-Fi radio. It is not TCP, not UDP, and not IP-based in the usual sense.

In this project, it is used as a direct board-to-board radio link.

### How ESP-NOW Works Here

The sender:

1. Puts the Wi-Fi radio into station mode.
2. Uses a fixed Wi-Fi channel, currently channel `1`.
3. Sends a binary packet directly to the receiver MAC address.

The receiver:

1. Also uses station mode.
2. Switches to the same Wi-Fi channel.
3. Registers an ESP-NOW receive callback.
4. Accepts the binary packet and validates it.

### Why The Channel Must Match

ESP-NOW frames travel on the Wi-Fi channel both devices are listening to. If the sender and receiver are not on the same channel, the radio link will fail even if the MAC addresses are correct.

### Why The Receiver MAC Matters

ESP-NOW can send to a specific peer MAC. In this project, the sender has a hardcoded `kReceiverMac` that must be updated after flashing the receiver and reading its startup log.

That is why the flashing order matters:

1. Flash receiver first.
2. Copy the printed receiver MAC.
3. Put that MAC into the sender firmware.
4. Flash sender second.

## Step 4: Receiver Validates And Queues The Packet

The receiver does not print directly from the ESP-NOW callback. Instead, it pushes incoming packets into a small ring buffer.

That matters because the ESP-NOW callback should stay fast. Serial printing is slower and can block, so the queue decouples wireless reception from USB output.

The receiver checks:

- Packet length matches the expected struct size
- Packet version matches `2`
- Packet data can be copied into the local struct safely

If the packet is invalid, the receiver emits an error JSON line and increments its counters.

Receiver implementation: [esp-receiver/src/main.cpp](../esp-receiver/src/main.cpp)

## Step 5: Receiver Converts Binary Data To NDJSON

After validation, the receiver prints one line of JSON per telemetry packet over USB serial.

This format is called NDJSON, short for newline-delimited JSON. It is a good fit for streaming because:

- Each telemetry sample is one independent line
- The browser can parse the stream incrementally
- Logs remain readable in the serial monitor

The main message types are:

- `receiver_ready` when the receiver boots and starts ESP-NOW
- `telemetry` for each valid packet
- `receiver_stats` for periodic health and queue information
- `error` for protocol, queue, or radio problems

### What A Telemetry Line Contains

The receiver adds fields that did not exist on the sender packet:

- `mac`: sender MAC address
- `receiverUptimeMs`: when the receiver saw the packet
- `rssi`: received signal strength, when available
- `raw`: nested RAW sensor diagnostics copied from the packet

The raw block is important because the browser dashboard and calibration workflow use it to understand what the sensors were actually outputting before any conversion.

The raw fields currently include:

- `tempAdc`, `phAdc`, `tdsAdc`, `turbidityAdc`
- `tempVoltage`, `phVoltage`, `tdsVoltage`, `turbidityVoltage`
- `flowPulseCount`, `flowWindowMs`

## Step 6: PC Dashboard Reads Serial Data

The dashboard is a browser app that connects to the receiver over Web Serial.

The flow on the PC is:

1. User clicks Connect Serial.
2. The browser opens the USB serial port.
3. The app filters boot noise and malformed startup lines.
4. Each JSON line is parsed as it arrives.
5. The live cards are updated with the latest telemetry.

Dashboard implementation: [web/app.js](../web/app.js)

The dashboard shows two views of the same data:

- Live measurements such as temperature, pH, flow, turbidity, and TDS
- RAW diagnostics such as ADC counts, voltages, and flow pulse timing

That design lets you see both the calibrated result and the sensor evidence behind it.

## Step 7: How The Dashboard Uses The Data

The browser does not invent values. It maps the receiver JSON directly into the UI:

- `temperature`, `ph`, `flow`, `turbidity`, and `tds` update the main metric cards
- `mac` and `sequence` show the most recent sender packet
- `raw.*` updates the calibration and diagnostics cards
- `receiver_stats` helps detect link health and queue issues

If the receiver stops delivering telemetry, the UI uses freshness and RSSI information to show link loss.

## End-To-End Data Path

Here is the full travel of one sensor sample:

1. A sensor or flow pulse changes a voltage or pulse count on the sender board.
2. The sender reads the raw value.
3. The sender converts raw readings into engineering units.
4. The sender stores both processed and raw values in `TelemetryPacket`.
5. ESP-NOW sends the binary packet to the receiver MAC on channel `1`.
6. The receiver accepts the frame and checks size and version.
7. The receiver queues the packet, then emits one NDJSON line over USB serial.
8. The PC browser reads the serial line.
9. The dashboard parses the JSON and updates the UI cards.
10. The operator sees both the final measurement and the raw calibration evidence.

## Why The RAW Fields Matter

The processed values are what you usually care about operationally, but RAW fields are what you need when the numbers look wrong.

For example:

- If pH looks clipped, the RAW pH ADC and voltage show whether the probe is saturating.
- If temperature is off, the thermistor ADC and voltage help verify the divider and calibration.
- If flow looks noisy, the pulse count and sample window explain the math behind the reported L/min.

This is why the dashboard keeps the RAW diagnostics visible instead of hiding them.

## Why The Receiver Is Flash First

The sender needs the receiver MAC address hardcoded into its firmware. That means the receiver must be running first so it can print its actual MAC.

If you change the packet format later, flash the receiver first again so it matches the sender’s packet layout before the sender starts transmitting.

## Common Failure Points

- Wrong receiver MAC in the sender firmware: ESP-NOW send fails.
- Channel mismatch: the radio link never forms.
- Packet version mismatch: receiver reports size or version errors.
- Serial browser not using HTTPS or localhost: Web Serial will not connect.
- Receiver queue overflow: the serial bridge cannot drain packets fast enough.

## Related Files

- [README.md](../README.md)
- [esp-sender/src/main.cpp](../esp-sender/src/main.cpp)
- [esp-receiver/src/main.cpp](../esp-receiver/src/main.cpp)
- [web/app.js](../web/app.js)
- [docs/FLASHING_GUIDE.md](FLASHING_GUIDE.md)
- [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
