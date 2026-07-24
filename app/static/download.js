const ACTIVE = new Set(["running", "paused_rate_limit"]);

async function fetchStatus() {
  const res = await fetch("/api/download/status");
  if (!res.ok) throw new Error("status " + res.status);
  return res.json();
}

async function startDownload() {
  const res = await fetch("/api/download/start", { method: "POST" });
  if (!res.ok) throw new Error("start " + res.status);
  return res.json();
}

async function stopDownload() {
  const res = await fetch("/api/download/stop", { method: "POST" });
  if (!res.ok) throw new Error("stop " + res.status);
  return res.json();
}

function formatStarted(iso) {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleString("ru-RU", { timeZone: "Asia/Novosibirsk" });
  } catch {
    return iso;
  }
}

function renderStatus(data) {
  const el = (id) => document.getElementById(id);
  if (!el("st-status")) return;

  el("st-status").textContent = data.status || "—";
  el("st-started").textContent = formatStarted(data.started_at_nsk);
  el("st-message").textContent = data.message || "—";
  el("st-counts").textContent =
    `N=${data.names_received}  M=${data.downloaded_count}  batch=${data.current_batch_size}`;
  el("st-error").textContent = data.error || "—";
}

let pollTimer = null;

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

function startPolling() {
  stopPolling();
  pollTimer = setInterval(async () => {
    try {
      const data = await fetchStatus();
      renderStatus(data);
      if (!ACTIVE.has(data.status)) stopPolling();
    } catch (e) {
      console.error(e);
    }
  }, 500);
}

async function onDownloadClick() {
  try {
    const data = await startDownload();
    renderStatus(data);
    startPolling();
  } catch (e) {
    alert("Не удалось запустить скачивание: " + e.message);
  }
}
async function onStopClick() {
  try {
    const data = await stopDownload();
    renderStatus(data);
    startPolling();
  } catch (e) {
    alert("Не удалось остановить: " + e.message);
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  const btn = document.getElementById("btn-download");
  const stopBtn = document.getElementById("btn-stop");

  if (btn) btn.addEventListener("click", onDownloadClick);
  if (stopBtn) stopBtn.addEventListener("click", onStopClick);

  try {
    const data = await fetchStatus();
    renderStatus(data);
    if (ACTIVE.has(data.status)) startPolling();
  } catch (e) {
    console.error(e);
  }
});


