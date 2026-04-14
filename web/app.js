const connectButton = document.getElementById("connectButton");
const disconnectButton = document.getElementById("disconnectButton");
const statusPill = document.getElementById("statusPill");
const envHint = document.getElementById("envHint");

const fields = {
  temperature: document.getElementById("temperature"),
  ph: document.getElementById("ph"),
  flow: document.getElementById("flow"),
  turbidity: document.getElementById("turbidity"),
  tds: document.getElementById("tds"),
  senderMac: document.getElementById("senderMac"),
  sequence: document.getElementById("sequence"),
  rssi: document.getElementById("rssi"),
  updatedAt: document.getElementById("updatedAt"),
};

const logOutput = document.getElementById("logOutput");
const kMaxLogLines = 220;

let port;
let reader;
let keepReading = false;
let textBuffer = "";
let readableClosed;
const logLines = [];
let ignoredBootLines = 0;

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

function updateTelemetry(data) {
  fields.temperature.textContent = Number(data.temperature).toFixed(2);
  fields.ph.textContent = Number(data.ph).toFixed(2);
  fields.flow.textContent = Number(data.flow).toFixed(2);
  fields.turbidity.textContent = Number(data.turbidity).toFixed(2);
  fields.tds.textContent = Number(data.tds).toFixed(2);
  fields.senderMac.textContent = data.mac || "-";
  fields.sequence.textContent = data.sequence ?? "-";
  fields.rssi.textContent = data.rssi ?? "-";
  fields.updatedAt.textContent = new Date().toLocaleTimeString();
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
    log(`Ignored malformed JSON line: ${line.slice(0, 120)}`);
    return;
  }

  if (payload.type === "telemetry") {
    updateTelemetry(payload);
    return;
  }

  if (payload.type === "receiver_ready") {
    log(`Receiver ready on ${payload.receiverMac}`);
    return;
  }

  if (payload.type === "receiver_stats") {
    log(
      `Stats total=${payload.total} valid=${payload.valid} invalid=${payload.invalid} dropped=${payload.dropped}`
    );
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

      textBuffer += value;
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

    keepReading = true;
    setControls(true);
    setStatus("status-connected", "Connected");
    log("Connected to serial port.");

    await readLoop();
    if (keepReading) {
      keepReading = false;
      setControls(false);
      setStatus("status-idle", "Idle");
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
updateEnvironmentHint();
log("Dashboard ready. Click Connect Serial to start.");
