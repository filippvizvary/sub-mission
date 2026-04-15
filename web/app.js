const connectButton = document.getElementById("connectButton");
const disconnectButton = document.getElementById("disconnectButton");
const statusPill = document.getElementById("statusPill");
const envHint = document.getElementById("envHint");
const signalFill = document.getElementById("signalFill");

const fields = {
  temperature: document.getElementById("temperature"),
  ph: document.getElementById("ph"),
  flow: document.getElementById("flow"),
  turbidity: document.getElementById("turbidity"),
  tds: document.getElementById("tds"),
  senderMac: document.getElementById("senderMac"),
  sequence: document.getElementById("sequence"),
  signalPercent: document.getElementById("signalPercent"),
  rssi: document.getElementById("rssi"),
  updatedAt: document.getElementById("updatedAt"),
  rawTempAdc: document.getElementById("rawTempAdc"),
  rawTempVoltage: document.getElementById("rawTempVoltage"),
  rawPhAdc: document.getElementById("rawPhAdc"),
  rawPhVoltage: document.getElementById("rawPhVoltage"),
  rawTdsAdc: document.getElementById("rawTdsAdc"),
  rawTdsVoltage: document.getElementById("rawTdsVoltage"),
  rawTurbidityAdc: document.getElementById("rawTurbidityAdc"),
  rawTurbidityVoltage: document.getElementById("rawTurbidityVoltage"),
  rawFlowPulses: document.getElementById("rawFlowPulses"),
  rawFlowWindowMs: document.getElementById("rawFlowWindowMs"),
};

const logOutput = document.getElementById("logOutput");
const kMaxLogLines = 220;
const kLinkLossThresholdMs = 4500;
const kStartupSyncWindowMs = 3500;
const kNoiseLogInterval = 20;
const kEstimateHoldMs = 1500;
const kSignalSmoothingAlpha = 0.28;
const kExpectedPacketVersion = 2;

let port;
let reader;
let keepReading = false;
let textBuffer = "";
let readableClosed;
let linkWatchdogId;
const logLines = [];
let ignoredBootLines = 0;
let malformedDuringSync = 0;
let serialSyncUntilMs = 0;
let lastTelemetryMs = 0;
let linkLost = false;
let hasSeenSender = false;
let serialSynced = false;
let smoothedSignalPercent = 0;
let hasWarnedRawMissing = false;

const kBootNoisePrefixes = [
  "rst:",
  "ets Jul",
  "configsip:",
  "clk_drv:",
  "mode:",
  "load:",
  "entry ",
];

function isBootNoise(line) {
  const trimmed = line.trim();
  if (!trimmed) {
    return false;
  }

  return kBootNoisePrefixes.some((prefix) => trimmed.startsWith(prefix));
}

function isLikelySerialNoise(line) {
  const trimmed = line.trim();
  if (!trimmed) {
    return false;
  }

  let printable = 0;
  for (let i = 0; i < trimmed.length; i += 1) {
    const code = trimmed.charCodeAt(i);
    if ((code >= 32 && code <= 126) || code === 9) {
      printable += 1;
    }
  }

  return printable / trimmed.length < 0.65;
}

function sanitizeChunk(text) {
  if (!text) {
    return "";
  }

  return text
    .replace(/\u0000/g, "")
    .replace(/[\uFFFD]/g, "")
    .replace(/[\x01-\x08\x0B\x0C\x0E-\x1F]/g, "");
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function rssiToPercent(rssi) {
  if (typeof rssi !== "number" || Number.isNaN(rssi)) {
    return null;
  }

  const mapped = ((rssi + 100) / 55) * 100;
  return Math.round(clamp(mapped, 0, 100));
}

function freshnessToPercent(ageMs) {
  if (ageMs <= kEstimateHoldMs) {
    return 100;
  }

  const effectiveAge = ageMs - kEstimateHoldMs;
  const effectiveWindow = Math.max(1, kLinkLossThresholdMs - kEstimateHoldMs);
  const mapped = 100 - (effectiveAge / effectiveWindow) * 100;
  return Math.round(clamp(mapped, 0, 100));
}

function smoothSignal(targetPercent) {
  const target = clamp(Number(targetPercent) || 0, 0, 100);
  smoothedSignalPercent =
    smoothedSignalPercent + (target - smoothedSignalPercent) * kSignalSmoothingAlpha;
  return Math.round(clamp(smoothedSignalPercent, 0, 100));
}

function resetSignalSmoothing(percent = 0) {
  smoothedSignalPercent = clamp(Number(percent) || 0, 0, 100);
}

function updateSignal(percent, rssiValue, options = {}) {
  const { skipSmoothing = false } = options;
  const clamped = skipSmoothing
    ? clamp(Number(percent) || 0, 0, 100)
    : smoothSignal(percent);
  fields.signalPercent.textContent = `${clamped}%`;
  if (signalFill) {
    signalFill.style.width = `${clamped}%`;
  }

  if (typeof rssiValue === "number" && Number.isFinite(rssiValue)) {
    fields.rssi.textContent = `RSSI: ${rssiValue} dBm`;
    return;
  }

  fields.rssi.textContent = "RSSI: Estimated";
}

function setLinkLost(active, reason) {
  if (linkLost === active) {
    return;
  }

  linkLost = active;
  document.body.classList.toggle("link-lost", active);
  if (active) {
    setStatus("status-error", "ESP-NOW Lost");
    log(reason || "ESP-NOW telemetry signal lost.");
  } else {
    setStatus("status-connected", "Connected");
    log("ESP-NOW telemetry signal restored.");
  }
}

function startWatchdog() {
  if (linkWatchdogId) {
    clearInterval(linkWatchdogId);
  }

  linkWatchdogId = setInterval(() => {
    if (!keepReading || !hasSeenSender || lastTelemetryMs === 0) {
      return;
    }

    const ageMs = Date.now() - lastTelemetryMs;
    updateSignal(freshnessToPercent(ageMs), null);

    if (ageMs > kLinkLossThresholdMs) {
      setLinkLost(true, "No telemetry received recently. Waiting for ESP-NOW link...");
      updateSignal(0, null, { skipSmoothing: true });
      resetSignalSmoothing(0);
      return;
    }

    if (linkLost) {
      setLinkLost(false);
    }
  }, 500);
}

function stopWatchdog() {
  if (linkWatchdogId) {
    clearInterval(linkWatchdogId);
    linkWatchdogId = undefined;
  }
}

function log(message) {
  const now = new Date().toLocaleTimeString();
  logLines.unshift(`[${now}] ${message}`);
  if (logLines.length > kMaxLogLines) {
    logLines.pop();
  }
  logOutput.textContent = logLines.join("\n");
}

function updateEnvironmentHint() {
  if (!envHint) {
    return;
  }

  if (!window.isSecureContext) {
    envHint.textContent = "Web Serial requires a secure origin. Open this dashboard using localhost or HTTPS.";
    return;
  }

  if (!("serial" in navigator)) {
    envHint.textContent = "Web Serial is unavailable in this browser. Use Chrome, Edge, or another Chromium-based browser.";
    return;
  }

  envHint.textContent = "Ready: secure origin detected and Web Serial is available.";
}

function setStatus(mode, text) {
  statusPill.classList.remove("status-idle", "status-connected", "status-error");
  statusPill.classList.add(mode);
  statusPill.textContent = text;
}

function setControls(connected) {
  connectButton.disabled = connected;
  disconnectButton.disabled = !connected;
}

function formatRawInt(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "-";
  }

  return Math.round(value).toString();
}

function formatRawVoltage(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "-";
  }

  return value.toFixed(3);
}

function formatMetric(value, digits = 2) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "-";
  }

  return value.toFixed(digits);
}

function updateTelemetry(data) {
  hasSeenSender = true;
  lastTelemetryMs = Date.now();
  setStatus("status-connected", "Connected");
  if (linkLost) {
    setLinkLost(false);
  }

  fields.temperature.textContent = formatMetric(data.temperature, 2);
  fields.ph.textContent = formatMetric(data.ph, 2);
  fields.flow.textContent = formatMetric(data.flow, 2);
  fields.turbidity.textContent = formatMetric(data.turbidity, 2);
  fields.tds.textContent = formatMetric(data.tds, 2);
  fields.senderMac.textContent = data.mac || "-";
  fields.sequence.textContent = data.sequence ?? "-";

  const rssiNumeric =
    typeof data.rssi === "number" && Number.isFinite(data.rssi) ? data.rssi : null;
  const quality =
    rssiNumeric !== null ? rssiToPercent(rssiNumeric) : freshnessToPercent(0);
  if (rssiNumeric !== null) {
    // Real RSSI should reflect quickly, so bypass smoothing.
    updateSignal(quality, rssiNumeric, { skipSmoothing: true });
    resetSignalSmoothing(quality);
  } else {
    updateSignal(quality, rssiNumeric);
  }

  fields.updatedAt.textContent = new Date().toLocaleTimeString();

  const raw = data.raw || {};
  if ((!data.raw || typeof data.raw !== "object") && !hasWarnedRawMissing) {
    log("Receiver is not sending raw diagnostics fields yet.");
    hasWarnedRawMissing = true;
  }
  fields.rawTempAdc.textContent = formatRawInt(raw.tempAdc);
  fields.rawTempVoltage.textContent = formatRawVoltage(raw.tempVoltage);
  fields.rawPhAdc.textContent = formatRawInt(raw.phAdc);
  fields.rawPhVoltage.textContent = formatRawVoltage(raw.phVoltage);
  fields.rawTdsAdc.textContent = formatRawInt(raw.tdsAdc);
  fields.rawTdsVoltage.textContent = formatRawVoltage(raw.tdsVoltage);
  fields.rawTurbidityAdc.textContent = formatRawInt(raw.turbidityAdc);
  fields.rawTurbidityVoltage.textContent = formatRawVoltage(raw.turbidityVoltage);
  fields.rawFlowPulses.textContent = formatRawInt(raw.flowPulseCount);
  fields.rawFlowWindowMs.textContent = formatRawInt(raw.flowWindowMs);
}

function processLine(line) {
  if (!line.trim()) {
    return;
  }

  if (isBootNoise(line)) {
    ignoredBootLines += 1;
    if (ignoredBootLines === 1 || ignoredBootLines % 25 === 0) {
      log(`Filtered ${ignoredBootLines} ESP boot/noise lines.`);
    }
    return;
  }

  let payload;
  try {
    payload = JSON.parse(line);
  } catch {
    if (
      !serialSynced ||
      Date.now() < serialSyncUntilMs ||
      isLikelySerialNoise(line)
    ) {
      malformedDuringSync += 1;
      if (
        malformedDuringSync === 1 ||
        malformedDuringSync % kNoiseLogInterval === 0
      ) {
        log(`Serial startup sync: filtered ${malformedDuringSync} malformed lines.`);
      }
      return;
    }

    log(`Ignored malformed JSON line: ${line.slice(0, 120)}`);
    return;
  }

  serialSynced = true;

  if (payload.type === "telemetry") {
    if (payload.version !== kExpectedPacketVersion) {
      log(
        `Protocol version mismatch: expected ${kExpectedPacketVersion}, got ${payload.version}.`
      );
    }
    updateTelemetry(payload);
    return;
  }

  if (payload.type === "receiver_ready") {
    log(`Receiver ready on ${payload.receiverMac}`);
    if (!hasSeenSender) {
      setStatus("status-idle", "Waiting for Sender");
    }
    return;
  }

  if (payload.type === "receiver_stats") {
    const lastPacketAgeMs =
      typeof payload.lastPacketAgeMs === "number" ? payload.lastPacketAgeMs : null;

    if (lastPacketAgeMs !== null) {
      hasSeenSender = true;
      lastTelemetryMs = Date.now() - lastPacketAgeMs;
      updateSignal(freshnessToPercent(lastPacketAgeMs), null);

      if (lastPacketAgeMs > kLinkLossThresholdMs) {
        setLinkLost(true, "Sender appears offline. Waiting for ESP-NOW telemetry...");
      } else if (linkLost) {
        setLinkLost(false);
      }
    }

    log(
      `Stats total=${payload.total} valid=${payload.valid} invalid=${payload.invalid} dropped=${payload.dropped} recentValid=${payload.recentValid ?? "-"}`
    );

    if (!hasSeenSender) {
      setStatus("status-idle", "Waiting for Sender");
    }

    return;
  }

  if (payload.type === "error") {
    setStatus("status-error", "Receiver Error");
    log(`Receiver error: ${payload.message}`);
  }
}

async function readLoop() {
  while (keepReading && reader) {
    try {
      const { value, done } = await reader.read();
      if (done) {
        break;
      }

      textBuffer += sanitizeChunk(value);
      const lines = textBuffer.split("\n");
      textBuffer = lines.pop() || "";

      for (const line of lines) {
        processLine(line);
      }
    } catch (error) {
      if (keepReading) {
        log(`Serial read failed: ${error.message}`);
      }
      break;
    }
  }
}

async function connectSerial() {
  if (!window.isSecureContext) {
    setStatus("status-error", "Secure Context Required");
    log("Open this page via localhost or HTTPS to use Web Serial.");
    updateEnvironmentHint();
    return;
  }

  if (!("serial" in navigator)) {
    setStatus("status-error", "Web Serial Unsupported");
    log("Use a Chromium browser with Web Serial support.");
    updateEnvironmentHint();
    return;
  }

  try {
    port = await navigator.serial.requestPort();
    await port.open({ baudRate: 115200 });

    if (!port.readable) {
      throw new Error("Selected serial port is not readable.");
    }

    const textDecoder = new TextDecoderStream();
    readableClosed = port.readable.pipeTo(textDecoder.writable).catch((error) => {
      if (keepReading) {
        log(`Serial stream closed unexpectedly: ${error.message}`);
      }
    });
    reader = textDecoder.readable.getReader();

    malformedDuringSync = 0;
    ignoredBootLines = 0;
    textBuffer = "";
    lastTelemetryMs = 0;
    hasSeenSender = false;
    hasWarnedRawMissing = false;
    serialSynced = false;
    serialSyncUntilMs = Date.now() + kStartupSyncWindowMs;

    keepReading = true;
    setControls(true);
    setStatus("status-idle", "Syncing Serial");
    document.body.classList.remove("link-lost");
    updateSignal(0, null);
    resetSignalSmoothing(0);
    startWatchdog();
    log("Connected to serial port.");

    await readLoop();
    if (keepReading) {
      keepReading = false;
      setControls(false);
      setStatus("status-idle", "Idle");
      stopWatchdog();
      log("Serial stream ended.");
    }
  } catch (error) {
    if (error?.name === "NotFoundError") {
      setStatus("status-idle", "Idle");
      log("Serial device selection was canceled.");
      return;
    }

    if (error?.name === "SecurityError") {
      setStatus("status-error", "Permission Blocked");
      log("Browser blocked serial access. Check site permissions and try again.");
      return;
    }

    setStatus("status-error", "Connection Failed");
    log(`Failed to connect: ${error.message}`);
  }
}

async function disconnectSerial(silent = false) {
  keepReading = false;
  stopWatchdog();
  setLinkLost(false);

  try {
    if (reader) {
      await reader.cancel().catch(() => {});
      reader.releaseLock();
      reader = undefined;
    }

    if (readableClosed) {
      await readableClosed.catch(() => {});
      readableClosed = undefined;
    }

    if (port) {
      await port.close();
      port = undefined;
    }

    setControls(false);
    setStatus("status-idle", "Idle");
    document.body.classList.remove("link-lost");
    hasSeenSender = false;
    serialSynced = false;
    lastTelemetryMs = 0;
    updateSignal(0, null, { skipSmoothing: true });
    resetSignalSmoothing(0);
    if (!silent) {
      log("Disconnected from serial port.");
    }
  } catch (error) {
    setStatus("status-error", "Disconnect Failed");
    log(`Failed to disconnect cleanly: ${error.message}`);
  }
}

connectButton.addEventListener("click", () => {
  connectSerial();
});

disconnectButton.addEventListener("click", () => {
  disconnectSerial();
});

if ("serial" in navigator) {
  navigator.serial.addEventListener("disconnect", (event) => {
    if (port && event.target === port) {
      setStatus("status-error", "Device Disconnected");
      log("Serial device was disconnected.");
      disconnectSerial(true);
    }
  });

  navigator.serial.addEventListener("connect", () => {
    log("A serial device became available.");
  });
}

setStatus("status-idle", "Idle");
updateSignal(0, null);
updateEnvironmentHint();
log("Dashboard ready. Click Connect Serial to start.");
