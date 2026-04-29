import argparse
import asyncio
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from threading import Lock
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import DEFAULT_CONFIG, AppConfig
from app.detector import BasicFaultDetector, FaultEvent
from app.event_log import EventLogger
from app.modbus_client import machine_client
from app.simulated_machine import SimulatedMachine


class MachineDataStore:
    def __init__(self, max_samples: int = 300, max_events: int = 100):
        self._lock = Lock()
        self._samples: deque[dict[str, Any]] = deque(maxlen=max_samples)
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._status: dict[str, Any] = {
            "connected": False,
            "source": "not_started",
            "last_error": None,
            "last_update": None,
        }

    def add_sample(self, values: dict[str, int], source: str) -> None:
        sample = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": source,
            "values": values,
        }
        with self._lock:
            self._samples.append(sample)
            self._status.update(
                {
                    "connected": True,
                    "source": source,
                    "last_error": None,
                    "last_update": sample["timestamp"],
                }
            )

    def add_events(self, events: list[FaultEvent]) -> None:
        with self._lock:
            for event in events:
                self._events.append(
                    {
                        "timestamp": event.timestamp.isoformat(timespec="seconds"),
                        "severity": event.severity,
                        "source": event.source,
                        "message": event.message,
                        "recommendation": event.recommendation,
                    }
                )

    def set_error(self, error: Exception, source: str) -> None:
        with self._lock:
            self._status.update(
                {
                    "connected": False,
                    "source": source,
                    "last_error": str(error),
                    "last_update": datetime.now().isoformat(timespec="seconds"),
                }
            )

    def current(self) -> dict[str, Any]:
        with self._lock:
            sample = self._samples[-1] if self._samples else None
            return {"status": self._status.copy(), "sample": sample}

    def history(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._samples)

    def events(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._events)


class Collector:
    def __init__(self, config: AppConfig, store: MachineDataStore, simulate: bool):
        self.config = config
        self.store = store
        self.simulate = simulate
        self.detector = BasicFaultDetector(config.registers)
        self.logger = EventLogger(config.event_log_path)
        self._stop = asyncio.Event()

    async def run(self) -> None:
        if self.simulate:
            await self._run_simulated()
            return

        while not self._stop.is_set():
            try:
                with machine_client(self.config) as machine:
                    await self._poll_machine(machine, "modbus")
            except Exception as error:
                self.store.set_error(error, "modbus")
                await asyncio.sleep(5)

    async def stop(self) -> None:
        self._stop.set()

    async def _run_simulated(self) -> None:
        machine = SimulatedMachine()
        await self._poll_machine(machine, "simulated")

    async def _poll_machine(self, machine: Any, source: str) -> None:
        while not self._stop.is_set():
            try:
                values = machine.read_registers()
                events = self.detector.inspect(values)
                for event in events:
                    self.logger.write(event)
                self.store.add_sample(values, source)
                self.store.add_events(events)
            except Exception as error:
                self.store.set_error(error, source)
                if source == "modbus":
                    raise
            await asyncio.sleep(self.config.poll_seconds)


def create_app(simulate: bool = False) -> FastAPI:
    config = DEFAULT_CONFIG
    store = MachineDataStore()
    collector = Collector(config, store, simulate)
    task: asyncio.Task[None] | None = None

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        nonlocal task
        task = asyncio.create_task(collector.run())
        try:
            yield
        finally:
            await collector.stop()
            if task:
                task.cancel()

    app = FastAPI(title="SMI AI Machine Monitor", lifespan=lifespan)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return DASHBOARD_HTML

    @app.get("/api/current")
    async def current() -> dict[str, Any]:
        return store.current()

    @app.get("/api/history")
    async def history() -> list[dict[str, Any]]:
        return store.history()

    @app.get("/api/events")
    async def events() -> list[dict[str, Any]]:
        return store.events()

    @app.get("/api/config")
    async def app_config() -> dict[str, Any]:
        return {
            "machine_ip": config.machine_ip,
            "machine_port": config.machine_port,
            "hmi_vnc_port": config.hmi_vnc_port,
            "hmi_web_port": config.hmi_web_port,
            "poll_seconds": config.poll_seconds,
            "unit_id": config.unit_id,
            "registers": [asdict(register) for register in config.registers],
            "simulate": simulate,
        }

    return app


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SMI AI Machine Monitor</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #eef2f3;
      --panel: #ffffff;
      --panel-soft: #f8faf9;
      --ink: #172321;
      --muted: #66736f;
      --line: #d8e0de;
      --ok: #16804a;
      --bad: #b8322a;
      --warn: #a05d00;
      --accent: #1e6b7d;
      --shadow: 0 1px 2px rgba(16, 24, 40, 0.07);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 14px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      box-shadow: var(--shadow);
      position: sticky;
      top: 0;
      z-index: 10;
    }
    h1 { margin: 0; font-size: 20px; line-height: 1.2; }
    .subtitle {
      color: var(--muted);
      font-size: 13px;
      margin-top: 3px;
    }
    main {
      width: min(1240px, 100%);
      margin: 0 auto;
      padding: 18px 18px 28px;
    }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 34px;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--panel-soft);
      font-weight: 700;
      font-size: 13px;
      color: var(--muted);
      white-space: nowrap;
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--bad);
    }
    .connected .dot { background: var(--ok); }
    .summary {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 14px;
      align-items: stretch;
      margin-bottom: 16px;
    }
    .summary-panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
      box-shadow: var(--shadow);
    }
    .summary-title {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }
    .summary-value {
      font-size: 24px;
      font-weight: 750;
      overflow-wrap: anywhere;
    }
    .summary-meta {
      color: var(--muted);
      font-size: 13px;
      margin-top: 7px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 13px;
      box-shadow: var(--shadow);
    }
    .label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
      margin-bottom: 7px;
      text-transform: uppercase;
    }
    .value {
      font-size: 28px;
      font-weight: 700;
      overflow-wrap: anywhere;
      line-height: 1.05;
    }
    .section-title {
      margin: 8px 0 10px;
      font-size: 17px;
      line-height: 1.2;
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-top: 4px;
    }
    .section-note {
      color: var(--muted);
      font-size: 13px;
    }
    .viewer {
      width: 100%;
      min-height: 540px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #111817;
      overflow: hidden;
      margin-bottom: 18px;
      box-shadow: var(--shadow);
    }
    .viewer iframe {
      display: block;
      width: 100%;
      height: 540px;
      border: 0;
    }
    .viewer-empty {
      padding: 16px;
      color: #c9d2d0;
    }
    .table-wrap {
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
    }
    th, td {
      padding: 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 14px;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      background: var(--panel-soft);
    }
    tbody tr:hover { background: #fbfcfc; }
    tr:last-child td { border-bottom: none; }
    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 3px 8px;
      background: #edf5f1;
      color: var(--ok);
      font-weight: 700;
      font-size: 12px;
      text-transform: capitalize;
    }
    .badge.warning { background: #fff6e5; color: var(--warn); }
    .badge.error { background: #fdeceb; color: var(--bad); }
    .error {
      color: var(--bad);
      font-weight: 700;
    }
    .muted { color: var(--muted); }
    @media (max-width: 640px) {
      header { align-items: flex-start; flex-direction: column; padding: 13px 14px; }
      main { padding: 14px; }
      .summary { grid-template-columns: 1fr; }
      .status { white-space: normal; }
      .value { font-size: 24px; }
      th, td { font-size: 13px; padding: 8px; }
      .viewer, .viewer iframe { min-height: 360px; height: 360px; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>SMI AI Machine Monitor</h1>
      <div class="subtitle">Thin-client data collection and HMI view</div>
    </div>
    <div id="status" class="status"><span class="dot"></span><span>Starting</span></div>
  </header>
  <main>
    <section class="summary">
      <article class="summary-panel">
        <div class="summary-title">Latest sample</div>
        <div id="sample-summary" class="summary-value">Waiting for data</div>
        <div id="sample-meta" class="summary-meta">No samples received yet</div>
      </article>
      <article class="summary-panel">
        <div class="summary-title">Machine source</div>
        <div id="source-summary" class="summary-value">--</div>
        <div id="source-meta" class="summary-meta">Polling status</div>
      </article>
    </section>
    <section id="cards" class="grid"></section>
    <div class="section-header">
      <h2 class="section-title">HMI Display</h2>
      <div class="section-note">Local VNC bridge on port 6080</div>
    </div>
    <section id="hmi-viewer" class="viewer">
      <div class="viewer-empty">Start the HMI web viewer to show the machine display here.</div>
    </section>
    <div class="section-header">
      <h2 class="section-title">Recent Events</h2>
      <div class="section-note">Newest first</div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>Time</th><th>Severity</th><th>Source</th><th>Message</th><th>Recommendation</th></tr>
        </thead>
        <tbody id="events"><tr><td colspan="5" class="muted">No events yet</td></tr></tbody>
      </table>
    </div>
  </main>
  <script>
    const cards = document.getElementById("cards");
    const status = document.getElementById("status");
    const eventsBody = document.getElementById("events");
    const hmiViewer = document.getElementById("hmi-viewer");
    const sampleSummary = document.getElementById("sample-summary");
    const sampleMeta = document.getElementById("sample-meta");
    const sourceSummary = document.getElementById("source-summary");
    const sourceMeta = document.getElementById("source-meta");
    let hmiLoaded = false;

    function formatName(name) {
      return name.replaceAll("_", " ");
    }

    function renderCards(sample) {
      const values = sample?.values || {};
      const entries = Object.entries(values);
      cards.innerHTML = entries.length
        ? entries.map(([name, value]) => `
          <article class="card">
            <div class="label">${formatName(name)}</div>
            <div class="value">${value}</div>
          </article>
        `).join("")
        : `<article class="card"><div class="label">Waiting for data</div><div class="value">--</div></article>`;
    }

    function renderStatus(payload) {
      const connected = payload.status.connected;
      status.className = connected ? "status connected" : "status";
      const last = payload.status.last_update || "no updates";
      const error = payload.status.last_error;
      status.innerHTML = `<span class="dot"></span><span>${connected ? "Connected" : "Disconnected"} - ${payload.status.source} - ${last}</span>`;
      sourceSummary.textContent = payload.status.source || "--";
      sourceMeta.textContent = connected ? `Last update ${last}` : (error || "Waiting for connection");
      if (error) {
        cards.insertAdjacentHTML("beforeend", `<article class="card"><div class="label">Last error</div><div class="value error">${error}</div></article>`);
      }
    }

    function renderSampleSummary(sample) {
      if (!sample) {
        sampleSummary.textContent = "Waiting for data";
        sampleMeta.textContent = "No samples received yet";
        return;
      }
      const count = Object.keys(sample.values || {}).length;
      const packageCount = sample.values?.package_count;
      sampleSummary.textContent = packageCount === undefined ? `${count} registers` : `Package ${packageCount}`;
      sampleMeta.textContent = `${count} registers - ${sample.timestamp}`;
    }

    function renderEvents(events) {
      const recent = [...events].reverse().slice(0, 12);
      eventsBody.innerHTML = recent.length
        ? recent.map(event => `
          <tr>
            <td>${event.timestamp}</td>
            <td><span class="badge ${event.severity}">${event.severity}</span></td>
            <td>${event.source}</td>
            <td>${event.message}</td>
            <td>${event.recommendation}</td>
          </tr>
        `).join("")
        : `<tr><td colspan="5" class="muted">No events yet</td></tr>`;
    }

    function renderHmi(config) {
      if (hmiLoaded) return;
      const webPort = config.hmi_web_port || 6080;
      const url = `${window.location.protocol}//${window.location.hostname}:${webPort}/vnc.html?autoconnect=1&resize=remote&reconnect=1`;
      hmiViewer.innerHTML = `<iframe title="HMI VNC display" src="${url}"></iframe>`;
      hmiLoaded = true;
    }

    async function refresh() {
      try {
        const [currentResponse, eventsResponse, configResponse] = await Promise.all([
          fetch("/api/current"),
          fetch("/api/events"),
          fetch("/api/config")
        ]);
        const current = await currentResponse.json();
        const events = await eventsResponse.json();
        const config = await configResponse.json();
        renderCards(current.sample);
        renderStatus(current);
        renderSampleSummary(current.sample);
        renderEvents(events);
        renderHmi(config);
      } catch (error) {
        status.className = "status";
        status.innerHTML = `<span class="dot"></span><span>Dashboard error</span>`;
      }
    }

    refresh();
    setInterval(refresh, 2000);
  </script>
</body>
</html>
"""


app = create_app(simulate=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SMI AI machine monitor dashboard")
    parser.add_argument("--simulate", action="store_true", help="Use generated machine data instead of Modbus TCP")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface for the web server")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    return parser.parse_args()


def main() -> None:
    import uvicorn

    args = parse_args()
    uvicorn.run(create_app(simulate=args.simulate), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
