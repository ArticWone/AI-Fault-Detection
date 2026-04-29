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
      --bg: #f4f7f6;
      --panel: #ffffff;
      --ink: #1c2524;
      --muted: #687674;
      --line: #d9e1df;
      --ok: #127a46;
      --bad: #b42318;
      --accent: #176b87;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      padding: 18px 22px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 { margin: 0; font-size: 22px; }
    main {
      width: min(1180px, 100%);
      margin: 0 auto;
      padding: 18px;
    }
    .status {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 700;
      color: var(--muted);
    }
    .dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--bad);
    }
    .connected .dot { background: var(--ok); }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }
    .label {
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 8px;
    }
    .value {
      font-size: 30px;
      font-weight: 700;
      overflow-wrap: anywhere;
    }
    .section-title {
      margin: 8px 0 10px;
      font-size: 17px;
    }
    .viewer {
      width: 100%;
      min-height: 540px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      overflow: hidden;
      margin-bottom: 18px;
    }
    .viewer iframe {
      display: block;
      width: 100%;
      height: 540px;
      border: 0;
    }
    .viewer-empty {
      padding: 16px;
      color: var(--muted);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
    }
    th, td {
      padding: 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      font-size: 14px;
      vertical-align: top;
    }
    th { color: var(--muted); font-weight: 700; }
    tr:last-child td { border-bottom: none; }
    .error {
      color: var(--bad);
      font-weight: 700;
    }
    .muted { color: var(--muted); }
    @media (max-width: 640px) {
      header { align-items: flex-start; flex-direction: column; }
      .value { font-size: 24px; }
      th, td { font-size: 13px; padding: 8px; }
      .viewer, .viewer iframe { min-height: 360px; height: 360px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>SMI AI Machine Monitor</h1>
    <div id="status" class="status"><span class="dot"></span><span>Starting</span></div>
  </header>
  <main>
    <section id="cards" class="grid"></section>
    <h2 class="section-title">HMI Display</h2>
    <section id="hmi-viewer" class="viewer">
      <div class="viewer-empty">Start the HMI web viewer to show the machine display here.</div>
    </section>
    <h2 class="section-title">Recent Events</h2>
    <table>
      <thead>
        <tr><th>Time</th><th>Severity</th><th>Source</th><th>Message</th><th>Recommendation</th></tr>
      </thead>
      <tbody id="events"><tr><td colspan="5" class="muted">No events yet</td></tr></tbody>
    </table>
  </main>
  <script>
    const cards = document.getElementById("cards");
    const status = document.getElementById("status");
    const eventsBody = document.getElementById("events");
    const hmiViewer = document.getElementById("hmi-viewer");
    let hmiLoaded = false;

    function renderCards(sample) {
      const values = sample?.values || {};
      const entries = Object.entries(values);
      cards.innerHTML = entries.length
        ? entries.map(([name, value]) => `
          <article class="card">
            <div class="label">${name.replaceAll("_", " ")}</div>
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
      status.innerHTML = `<span class="dot"></span><span>${connected ? "Connected" : "Disconnected"} · ${payload.status.source} · ${last}</span>`;
      if (error) {
        cards.insertAdjacentHTML("beforeend", `<article class="card"><div class="label">Last error</div><div class="value error">${error}</div></article>`);
      }
    }

    function renderEvents(events) {
      const recent = [...events].reverse().slice(0, 12);
      eventsBody.innerHTML = recent.length
        ? recent.map(event => `
          <tr>
            <td>${event.timestamp}</td>
            <td>${event.severity}</td>
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
