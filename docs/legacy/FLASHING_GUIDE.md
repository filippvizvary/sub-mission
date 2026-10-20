# Flashing Guide

Always flash receiver first, then sender.

## 1. Flash Receiver

```bash
cd /home/filip/sub-mission/esp-receiver
pio run -t upload
pio device monitor -b 115200
```

Expected startup message:

```json
{"type":"receiver_ready","packetVersion":2,"receiverMac":"..","baud":115200}
```

Copy the `receiverMac` value.

## 2. Set Sender Target MAC

Open `esp-sender/src/main.cpp` and set `kReceiverMac` to the receiver MAC printed above.

## 3. Flash Sender

```bash
cd /home/filip/sub-mission/esp-sender
pio run -t upload
pio device monitor -b 115200
```

Expected sender logs include:

- `type=sender_ready` with `packetVersion=2`
- `type=sender_peer_target`
- `type=sender_peer_added`
- `type=sender_send` status mostly `ok`

## 4. Start Dashboard

```bash
cd /home/filip/sub-mission/web
python3 -m http.server 8080
```

Open `http://localhost:8080` in Chrome/Edge/Brave and click Connect Serial.

## 5. Flashing Order Rule

When protocol changes:

1. Flash receiver first.
2. Flash sender second.

If versions mismatch, receiver will report packet size/version errors and telemetry will not update.
