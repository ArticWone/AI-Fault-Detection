import argparse
import asyncio
import os
import shlex
import subprocess
import sys
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, Response

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

    def add_event(self, event: FaultEvent) -> None:
        self.add_events([event])

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


class HmiSnapshotStore:
    def __init__(self, config: AppConfig, simulate: bool):
        self.config = config
        self.simulate = simulate
        self.directory = self._snapshot_directory()
        self.directory.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[dict[str, Any]]:
        snapshots: list[dict[str, Any]] = []
        for path in sorted(self.directory.glob("hmi_snapshot_*"), reverse=True):
            if not path.is_file():
                continue
            snapshots.append(self._metadata(path))
        return snapshots

    def capture(self) -> dict[str, Any]:
        timestamp = datetime.now()
        suffix = "svg" if self.simulate else "png"
        path = self.directory / f"hmi_snapshot_{timestamp.strftime('%Y%m%d_%H%M%S')}.{suffix}"

        if self.simulate:
            self._write_simulated_snapshot(path, timestamp)
        else:
            self._capture_vnc_snapshot(path)

        return self._metadata(path)

    def path_for(self, filename: str) -> Path:
        if "/" in filename or "\\" in filename:
            raise ValueError("Invalid snapshot filename")
        path = self.directory / filename
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(filename)
        return path

    def _capture_vnc_snapshot(self, path: Path) -> None:
        server = f"{self.config.machine_ip}::{self.config.hmi_vnc_port}"
        command = ["vncdotool", "-s", server]
        password = os.environ.get("SMI_HMI_VNC_PASSWORD")
        if password:
            command.extend(["-p", password])
        command.extend(["capture", str(path)])

        result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "HMI snapshot capture failed").strip()
            raise RuntimeError(detail)

    def _metadata(self, path: Path) -> dict[str, Any]:
        stat = path.stat()
        return {
            "filename": path.name,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "size_bytes": stat.st_size,
            "url": f"/api/snapshots/{path.name}",
            "download_url": f"/api/snapshots/{path.name}?download=1",
        }

    def _snapshot_directory(self) -> Path:
        root = Path(os.environ.get("SMI_AI_DATA_ROOT", "/srv/smi-ai"))
        if not root.exists() and os.name == "nt":
            root = Path("data")
        return root / "hmi_snapshots"

    def _write_simulated_snapshot(self, path: Path, timestamp: datetime) -> None:
        path.write_text(
            f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
  <rect width="960" height="540" fill="#111817"/>
  <rect x="42" y="38" width="876" height="464" rx="8" fill="#172321" stroke="#5d6f6b"/>
  <text x="80" y="102" fill="#dfe8e6" font-family="Arial, sans-serif" font-size="38" font-weight="700">Simulated HMI Snapshot</text>
  <text x="80" y="156" fill="#91a4a0" font-family="Arial, sans-serif" font-size="24">{timestamp.isoformat(timespec="seconds")}</text>
  <rect x="80" y="222" width="220" height="94" rx="6" fill="#20312e" stroke="#5d6f6b"/>
  <rect x="370" y="222" width="220" height="94" rx="6" fill="#20312e" stroke="#5d6f6b"/>
  <rect x="660" y="222" width="220" height="94" rx="6" fill="#20312e" stroke="#5d6f6b"/>
  <text x="110" y="280" fill="#dfe8e6" font-family="Arial, sans-serif" font-size="26">RUN</text>
  <text x="400" y="280" fill="#dfe8e6" font-family="Arial, sans-serif" font-size="26">COUNT</text>
  <text x="690" y="280" fill="#dfe8e6" font-family="Arial, sans-serif" font-size="26">OK</text>
  <circle cx="848" cy="104" r="18" fill="#16804a"/>
</svg>
""",
            encoding="utf-8",
        )


class CameraPreviewStore:
    def __init__(self):
        self.env = self._load_camera_env()
        self.user = self.env.get("SMI_CAMERA_USER", os.environ.get("SMI_CAMERA_USER", "admin"))
        self.password = self.env.get("SMI_CAMERA_PASSWORD", os.environ.get("SMI_CAMERA_PASSWORD", ""))
        self.port = self.env.get("SMI_CAMERA_RTSP_PORT", os.environ.get("SMI_CAMERA_RTSP_PORT", "554"))
        self.stream = self.env.get("SMI_CAMERA_STREAM", os.environ.get("SMI_CAMERA_STREAM", "main"))
        self.path_prefix = self.env.get(
            "SMI_CAMERA_RTSP_PATH_PREFIX",
            os.environ.get("SMI_CAMERA_RTSP_PATH_PREFIX", "Preview_01_"),
        )
        self.cameras = self._parse_cameras(self.env.get("SMI_CAMERAS", os.environ.get("SMI_CAMERAS", "")))
        self.admin_urls = self._parse_cameras(
            self.env.get("SMI_CAMERA_ADMIN_URLS", os.environ.get("SMI_CAMERA_ADMIN_URLS", ""))
        )
        self.snapshot_directory = self._snapshot_directory()
        self.snapshot_directory.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[dict[str, Any]]:
        return [
            {
                "id": camera_id,
                "host": host,
                "stream": self.stream,
                "admin_url": self.admin_urls.get(camera_id, f"http://{host}/"),
                "snapshot_url": f"/api/cameras/{camera_id}/snapshot",
                "webrtc_path": f"/stream.html?src={camera_id}&mode=webrtc",
            }
            for camera_id, host in self.cameras.items()
        ]

    def snapshot(self, camera_id: str) -> bytes:
        host = self.cameras.get(camera_id)
        if not host:
            raise KeyError(camera_id)
        if not self.password:
            raise RuntimeError("Camera password is not configured")

        url = self._rtsp_url(host)
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-rtsp_transport",
            "tcp",
            "-i",
            url,
            "-frames:v",
            "1",
            "-an",
            "-f",
            "image2pipe",
            "-vcodec",
            "mjpeg",
            "pipe:1",
        ]
        result = subprocess.run(command, capture_output=True, timeout=15, check=False)
        if result.returncode != 0 or not result.stdout:
            detail = (result.stderr.decode("utf-8", errors="replace") or "Camera snapshot failed").strip()
            raise RuntimeError(detail)
        return result.stdout

    def capture_bad_packs(self) -> dict[str, Any]:
        if not self.cameras:
            raise RuntimeError("No camera is configured")

        camera_id = next(iter(self.cameras))
        return self.capture_saved_snapshot(camera_id, "bad_packs")

    def capture_saved_snapshot(self, camera_id: str, prefix: str = "camera_snapshot") -> dict[str, Any]:
        if camera_id not in self.cameras:
            raise KeyError(camera_id)

        timestamp = datetime.now()
        image = self.snapshot(camera_id)
        path = self.snapshot_directory / f"{prefix}_{camera_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        path.write_bytes(image)
        return self._metadata(path, camera_id)

    def path_for(self, filename: str) -> Path:
        if "/" in filename or "\\" in filename:
            raise ValueError("Invalid camera snapshot filename")
        path = self.snapshot_directory / filename
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(filename)
        return path

    def _metadata(self, path: Path, camera_id: str | None = None) -> dict[str, Any]:
        stat = path.stat()
        if camera_id is None and path.stem.startswith("bad_packs_"):
            camera_id = path.stem.removeprefix("bad_packs_").rsplit("_", 2)[0]
        return {
            "filename": path.name,
            "camera_id": camera_id,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "size_bytes": stat.st_size,
            "url": f"/api/camera-snapshots/{path.name}",
            "download_url": f"/api/camera-snapshots/{path.name}?download=1",
        }

    def _snapshot_directory(self) -> Path:
        root = Path(os.environ.get("SMI_AI_DATA_ROOT", "/srv/smi-ai"))
        if not root.exists() and os.name == "nt":
            root = Path("data")
        return root / "camera_snapshots"

    def _load_camera_env(self) -> dict[str, str]:
        env_file = Path(os.environ.get("SMI_CAMERA_ENV", "/srv/smi-ai/config/cameras.env"))
        if not env_file.exists():
            return {}

        parsed: dict[str, str] = {}
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            parsed[key.strip()] = shlex.split(value, comments=False, posix=True)[0] if value.strip() else ""
        return parsed

    def _parse_cameras(self, value: str) -> dict[str, str]:
        cameras: dict[str, str] = {}
        for item in value.split():
            if "=" not in item:
                continue
            camera_id, host = item.split("=", 1)
            if camera_id and host:
                cameras[camera_id] = host
        return cameras

    def _rtsp_url(self, host: str) -> str:
        return f"rtsp://{self.user}:{self.password}@{host}:{self.port}/{self.path_prefix}{self.stream}"


class RecordingStore:
    def __init__(self):
        self.directory = self._recording_directory()
        self.directory.mkdir(parents=True, exist_ok=True)

    def list(self, limit: int = 12) -> list[dict[str, Any]]:
        recordings: list[dict[str, Any]] = []
        paths = sorted(
            list(self.directory.glob("*/*/*.mkv")) + list(self.directory.glob("*/*/*.mp4")),
            key=lambda path: path.stat().st_mtime if path.is_file() else 0,
            reverse=True,
        )
        for path in paths[:limit]:
            if path.is_file():
                recordings.append(self._metadata(path))
        return recordings

    def path_for(self, camera_id: str, day: str, filename: str) -> Path:
        for value in (camera_id, day, filename):
            if "/" in value or "\\" in value or value in {"", ".", ".."}:
                raise ValueError("Invalid recording path")
        if not filename.endswith((".mkv", ".mp4")):
            raise ValueError("Invalid recording filename")

        path = self.directory / camera_id / day / filename
        try:
            path.relative_to(self.directory)
        except ValueError as error:
            raise ValueError("Invalid recording path") from error
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(filename)
        return path

    def _metadata(self, path: Path) -> dict[str, Any]:
        stat = path.stat()
        camera_id = path.parent.parent.name
        day = path.parent.name
        return {
            "filename": path.name,
            "camera_id": camera_id,
            "day": day,
            "created": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            "size_bytes": stat.st_size,
            "url": f"/api/recordings/{camera_id}/{day}/{path.name}",
            "download_url": f"/api/recordings/{camera_id}/{day}/{path.name}?download=1",
        }

    def _recording_directory(self) -> Path:
        root = Path(os.environ.get("SMI_VIDEO_ROOT", "/srv/smi-ai/video"))
        if not root.exists() and os.name == "nt":
            root = Path("data") / "video"
        return root


def create_app(simulate: bool = False) -> FastAPI:
    config = DEFAULT_CONFIG
    store = MachineDataStore()
    snapshots = HmiSnapshotStore(config, simulate)
    cameras = CameraPreviewStore()
    recordings = RecordingStore()
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

    @app.post("/api/faults/manual")
    async def mark_manual_fault() -> dict[str, str]:
        event = FaultEvent(
            datetime.now(),
            "error",
            "operator",
            "Manual fault marked",
            "Review the machine state and capture supporting HMI/camera evidence.",
        )
        collector.logger.write(event)
        store.add_event(event)
        return {"status": "marked"}

    @app.get("/api/snapshots")
    async def list_snapshots() -> list[dict[str, Any]]:
        return snapshots.list()

    @app.post("/api/snapshots")
    async def capture_snapshot() -> dict[str, Any]:
        try:
            return await asyncio.to_thread(snapshots.capture)
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

    @app.get("/api/snapshots/{filename}")
    async def get_snapshot(filename: str, download: bool = False) -> FileResponse:
        try:
            path = snapshots.path_for(filename)
        except (ValueError, FileNotFoundError) as error:
            raise HTTPException(status_code=404, detail="Snapshot not found") from error

        media_type = "image/svg+xml" if path.suffix == ".svg" else "image/png"
        return FileResponse(path, media_type=media_type, filename=path.name if download else None)

    @app.get("/api/cameras")
    async def list_cameras() -> list[dict[str, Any]]:
        return cameras.list()

    @app.get("/api/cameras/{camera_id}/snapshot")
    async def camera_snapshot(camera_id: str) -> Response:
        try:
            image = await asyncio.to_thread(cameras.snapshot, camera_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Camera not found") from error
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

        return Response(
            content=image,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store, max-age=0"},
        )

    @app.post("/api/cameras/bad-packs")
    async def capture_bad_packs() -> dict[str, Any]:
        try:
            snapshot = await asyncio.to_thread(cameras.capture_bad_packs)
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

        event = FaultEvent(
            datetime.now(),
            "error",
            "bad_packs",
            "Bad pack(s) camera snapshot captured",
            f"Review camera snapshot {snapshot['filename']}.",
        )
        collector.logger.write(event)
        store.add_event(event)
        return snapshot

    @app.post("/api/cameras/{camera_id}/snapshots")
    async def capture_camera_snapshot(camera_id: str) -> dict[str, Any]:
        try:
            snapshot = await asyncio.to_thread(cameras.capture_saved_snapshot, camera_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail="Camera not found") from error
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error

        event = FaultEvent(
            datetime.now(),
            "info",
            "camera",
            f"Camera snapshot captured from {camera_id}",
            f"Review camera snapshot {snapshot['filename']}.",
        )
        collector.logger.write(event)
        store.add_event(event)
        return snapshot

    @app.get("/api/camera-snapshots/{filename}")
    async def get_camera_snapshot(filename: str, download: bool = False) -> FileResponse:
        try:
            path = cameras.path_for(filename)
        except (ValueError, FileNotFoundError) as error:
            raise HTTPException(status_code=404, detail="Camera snapshot not found") from error

        return FileResponse(path, media_type="image/jpeg", filename=path.name if download else None)

    @app.get("/api/recordings")
    async def list_recordings(limit: int = 12) -> list[dict[str, Any]]:
        safe_limit = max(1, min(limit, 50))
        return recordings.list(safe_limit)

    @app.get("/api/recordings/{camera_id}/{day}/{filename}")
    async def get_recording(camera_id: str, day: str, filename: str, download: bool = False) -> FileResponse:
        try:
            path = recordings.path_for(camera_id, day, filename)
        except (ValueError, FileNotFoundError) as error:
            raise HTTPException(status_code=404, detail="Recording not found") from error

        return FileResponse(
            path,
            media_type="video/mp4" if path.suffix == ".mp4" else "video/x-matroska",
            filename=path.name if download else None,
        )

    @app.post("/api/system/shutdown")
    async def shutdown_node() -> dict[str, str]:
        event = FaultEvent(
            datetime.now(),
            "warning",
            "system",
            "Node shutdown requested from Web UI",
            "The node is shutting down. Physical access or Wake-on-LAN may be required to bring it back.",
        )
        collector.logger.write(event)
        store.add_event(event)

        command = ["shutdown", "-h", "now"] if sys.platform != "win32" else ["shutdown", "/s", "/t", "0"]
        try:
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error)) from error
        return {"status": "shutdown_requested"}

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
      padding: 18px 18px 92px;
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
    .card-button {
      display: block;
      width: 100%;
      min-height: 100%;
      border: 0;
      border-radius: 8px;
      padding: 13px;
      text-align: left;
      font: inherit;
      cursor: pointer;
      box-shadow: var(--shadow);
    }
    .card-button.centered {
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
    }
    .card-button.fault {
      background: #b3261e;
      color: #ffffff;
    }
    .card-button.bad-packs {
      background: #ffd84d;
      border: 2px solid #c99700;
      color: #1f250f;
    }
    .card-button.fault .label,
    .card-button.fault .value,
    .card-button.bad-packs .value {
      color: inherit;
    }
    .card-button.fault .value,
    .card-button.bad-packs .value {
      text-transform: uppercase;
    }
    .card-button.fault:disabled {
      cursor: wait;
      opacity: 0.75;
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
      align-items: center;
      gap: 12px;
      margin-top: 4px;
    }
    .section-actions {
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }
    .section-note {
      color: var(--muted);
      font-size: 13px;
    }
    button {
      appearance: none;
      border: 1px solid var(--accent);
      border-radius: 8px;
      background: var(--accent);
      color: #ffffff;
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      font-weight: 700;
      min-height: 36px;
      padding: 8px 12px;
    }
    button.secondary {
      background: var(--panel);
      color: var(--accent);
    }
    button:disabled {
      cursor: wait;
      opacity: 0.65;
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
      margin-bottom: 18px;
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
    .download-link {
      color: var(--accent);
      font-size: 13px;
      font-weight: 700;
      text-decoration: none;
      white-space: nowrap;
    }
    .action-message {
      color: var(--muted);
      font-size: 13px;
      min-height: 18px;
      margin: -8px 0 14px;
    }
    .camera-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }
    .camera-panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }
    .camera-panel img {
      display: block;
      width: 100%;
      aspect-ratio: 16 / 9;
      background: #111817;
      object-fit: cover;
    }
    .camera-panel iframe {
      display: block;
      width: 100%;
      aspect-ratio: 16 / 9;
      border: 0;
      background: #111817;
    }
    .camera-meta {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      font-size: 13px;
    }
    .camera-name {
      font-weight: 750;
      overflow-wrap: anywhere;
    }
    .camera-card-actions {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .camera-admin-link {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 30px;
      padding: 6px 10px;
      border: 1px solid var(--accent);
      border-radius: 8px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 750;
      text-decoration: none;
      white-space: nowrap;
    }
    .camera-snapshot-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 30px;
      padding: 6px 10px;
      border: 1px solid var(--accent);
      border-radius: 8px;
      background: var(--panel);
      color: var(--accent);
      font-size: 12px;
      font-weight: 750;
      white-space: nowrap;
      cursor: pointer;
    }
    .camera-snapshot-button:disabled {
      cursor: wait;
      opacity: 0.65;
    }
    .recordings-actions {
      display: inline-flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .shutdown-dock {
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 20;
      display: flex;
      justify-content: center;
      padding: 10px 16px calc(10px + env(safe-area-inset-bottom));
      background: rgba(238, 242, 243, 0.94);
      border-top: 1px solid var(--line);
      backdrop-filter: blur(8px);
    }
    .shutdown-button {
      min-width: min(420px, 100%);
      min-height: 42px;
      border: 1px solid #8f211b;
      border-radius: 8px;
      background: #b3261e;
      color: #ffffff;
      font-weight: 800;
      font-size: 14px;
      text-transform: uppercase;
      cursor: pointer;
    }
    .modal-backdrop {
      position: fixed;
      inset: 0;
      z-index: 30;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 18px;
      background: rgba(17, 24, 23, 0.55);
    }
    .modal-backdrop.open { display: flex; }
    .confirm-modal {
      width: min(420px, 100%);
      border-radius: 8px;
      border: 1px solid var(--line);
      background: var(--panel);
      box-shadow: 0 18px 48px rgba(16, 24, 40, 0.25);
      padding: 18px;
    }
    .confirm-modal h2 {
      margin: 0 0 8px;
      font-size: 20px;
    }
    .confirm-modal p {
      margin: 0 0 16px;
      color: var(--muted);
      line-height: 1.35;
    }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      flex-wrap: wrap;
    }
    .modal-actions button {
      min-height: 38px;
      border-radius: 8px;
      padding: 8px 12px;
      font-weight: 800;
      cursor: pointer;
    }
    .cancel-shutdown {
      border: 1px solid var(--line);
      background: var(--panel-soft);
      color: var(--ink);
    }
    .confirm-shutdown {
      border: 1px solid #8f211b;
      background: #b3261e;
      color: #ffffff;
    }
    @media (max-width: 640px) {
      header { align-items: flex-start; flex-direction: column; padding: 13px 14px; }
      main { padding: 14px; }
      .summary { grid-template-columns: 1fr; }
      .status { white-space: normal; }
      .section-header { align-items: flex-start; flex-direction: column; }
      .section-actions { width: 100%; justify-content: space-between; }
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
      <div class="section-actions">
        <div class="section-note">Local VNC bridge on port 6080</div>
        <button id="snapshot-button" type="button">Snapshot</button>
      </div>
    </div>
    <section id="hmi-viewer" class="viewer">
      <div class="viewer-empty">Start the HMI web viewer to show the machine display here.</div>
    </section>
    <div class="section-header">
      <h2 class="section-title">Camera Preview</h2>
      <div class="section-actions">
        <div class="section-note">WebRTC via go2rtc</div>
        <button id="camera-snapshot-button" type="button">Snapshot</button>
      </div>
    </div>
    <section id="camera-preview" class="camera-grid">
      <article class="card"><div class="label">Camera</div><div class="value">--</div></article>
    </section>
    <div class="section-header">
      <h2 class="section-title">Camera Recordings</h2>
      <button id="refresh-recordings" class="secondary" type="button">Refresh</button>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>Time</th><th>Camera</th><th>File</th><th>Size</th><th>Action</th></tr>
        </thead>
        <tbody id="recordings"><tr><td colspan="5" class="muted">No recordings found</td></tr></tbody>
      </table>
    </div>
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
    <div class="section-header">
      <h2 class="section-title">HMI Snapshots</h2>
      <button id="view-more-snapshots" class="secondary" type="button" hidden>View more</button>
    </div>
    <div id="snapshot-message" class="action-message"></div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>Time</th><th>File</th><th>Size</th><th>Action</th></tr>
        </thead>
        <tbody id="snapshots"><tr><td colspan="4" class="muted">No snapshots yet</td></tr></tbody>
      </table>
    </div>
  </main>
  <div class="shutdown-dock">
    <button id="shutdown-button" class="shutdown-button" type="button">Shutdown Node</button>
  </div>
  <div id="shutdown-modal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="shutdown-title">
    <div class="confirm-modal">
      <h2 id="shutdown-title">Shut down node?</h2>
      <p>This will power off the node and the Web UI will disconnect. Make sure recording and checks are finished first.</p>
      <div class="modal-actions">
        <button id="cancel-shutdown" class="cancel-shutdown" type="button">Cancel</button>
        <button id="confirm-shutdown" class="confirm-shutdown" type="button">Yes, shut down node</button>
      </div>
    </div>
  </div>
  <script>
    const cards = document.getElementById("cards");
    const status = document.getElementById("status");
    const eventsBody = document.getElementById("events");
    const hmiViewer = document.getElementById("hmi-viewer");
    const snapshotButton = document.getElementById("snapshot-button");
    const cameraSnapshotButton = document.getElementById("camera-snapshot-button");
    const snapshotMessage = document.getElementById("snapshot-message");
    const snapshotsEl = document.getElementById("snapshots");
    const viewMoreSnapshots = document.getElementById("view-more-snapshots");
    const cameraPreview = document.getElementById("camera-preview");
    const refreshRecordingsButton = document.getElementById("refresh-recordings");
    const recordingsEl = document.getElementById("recordings");
    const sampleSummary = document.getElementById("sample-summary");
    const sampleMeta = document.getElementById("sample-meta");
    const sourceSummary = document.getElementById("source-summary");
    const sourceMeta = document.getElementById("source-meta");
    const shutdownButton = document.getElementById("shutdown-button");
    const shutdownModal = document.getElementById("shutdown-modal");
    const cancelShutdown = document.getElementById("cancel-shutdown");
    const confirmShutdown = document.getElementById("confirm-shutdown");
    let hmiLoaded = false;
    let showAllSnapshots = false;
    let renderedCameraKey = "";
    let activeCameras = [];

    function formatName(name) {
      return name.replaceAll("_", " ");
    }

    function orderedCardEntries(values) {
      const preferred = ["format", "set_format", "package_count", "lot_number"];
      const entries = Object.entries(values);
      const known = preferred
        .filter(name => Object.prototype.hasOwnProperty.call(values, name))
        .map(name => [name, values[name]]);
      const rest = entries.filter(([name]) => !preferred.includes(name));
      return [...known, ...rest];
    }

    function renderCards(sample) {
      const values = sample?.values || {};
      const entries = orderedCardEntries(values);
      cards.innerHTML = entries.length
        ? entries.map(([name, value]) => `
          ${name === "lot_number" ? `
            <button class="card-button fault centered" type="button" data-action="mark-manual-fault" aria-label="Mark manual fault">
              <div class="value">FAULT</div>
            </button>
          ` : name === "package_count" ? `
            <button class="card-button bad-packs centered" type="button" data-action="capture-bad-packs" aria-label="Capture bad pack camera snapshot">
              <div class="value">BAD PACK(S)</div>
            </button>
          ` : `
            <article class="card">
              <div class="label">${formatName(name)}</div>
              <div class="value">${value}</div>
            </article>
          `}
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

    function renderSnapshots(snapshots) {
      const visible = showAllSnapshots ? snapshots : snapshots.slice(0, 3);
      viewMoreSnapshots.hidden = snapshots.length <= 3;
      viewMoreSnapshots.textContent = showAllSnapshots ? "Show latest 3" : `View more (${snapshots.length})`;
      snapshotsEl.innerHTML = visible.length
        ? visible.map(snapshot => `
          <tr>
            <td>${snapshot.created}</td>
            <td>${snapshot.filename}</td>
            <td>${Math.round(snapshot.size_bytes / 1024)} KB</td>
            <td><a class="download-link" href="${snapshot.download_url}" download>Download</a></td>
          </tr>
        `).join("")
        : `<tr><td colspan="4" class="muted">No snapshots yet</td></tr>`;
    }

    function formatBytes(bytes) {
      if (bytes >= 1024 * 1024 * 1024) return `${(bytes / 1024 / 1024 / 1024).toFixed(1)} GB`;
      if (bytes >= 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
      if (bytes >= 1024) return `${Math.round(bytes / 1024)} KB`;
      return `${bytes} B`;
    }

    function renderRecordings(recordings) {
      recordingsEl.innerHTML = recordings.length
        ? recordings.map(recording => `
          <tr>
            <td>${recording.created}</td>
            <td>${recording.camera_id}</td>
            <td>${recording.filename}</td>
            <td>${formatBytes(recording.size_bytes)}</td>
            <td>
              <span class="recordings-actions">
                <a class="download-link" href="${recording.url}" target="_blank" rel="noreferrer">Open</a>
                <a class="download-link" href="${recording.download_url}" download>Download</a>
              </span>
            </td>
          </tr>
        `).join("")
        : `<tr><td colspan="5" class="muted">No recordings found</td></tr>`;
    }

    function renderCameras(cameras) {
      activeCameras = cameras;
      cameraSnapshotButton.disabled = cameras.length === 0;
      const cameraKey = cameras.map(camera => `${camera.id}:${camera.host}:${camera.stream}:${camera.admin_url}`).join("|");
      if (cameraKey === renderedCameraKey) return;
      renderedCameraKey = cameraKey;

      cameraPreview.innerHTML = cameras.length
        ? cameras.map(camera => `
          <article class="camera-panel">
            <iframe src="${window.location.protocol}//${window.location.hostname}:1984${camera.webrtc_path}" title="${camera.id} WebRTC preview" allow="autoplay; fullscreen"></iframe>
            <div class="camera-meta">
              <span class="camera-name">${camera.id}</span>
              <span class="camera-card-actions">
                <span class="muted">${camera.host} - ${camera.stream}</span>
                <a class="camera-admin-link" href="${camera.admin_url}" target="_blank" rel="noreferrer">Admin</a>
              </span>
            </div>
          </article>
        `).join("")
        : `<article class="card"><div class="label">Camera</div><div class="value">--</div></article>`;
    }

    async function refreshSnapshots() {
      const response = await fetch("/api/snapshots");
      const snapshots = await response.json();
      renderSnapshots(snapshots);
    }

    async function refreshRecordings() {
      refreshRecordingsButton.disabled = true;
      try {
        const response = await fetch("/api/recordings?limit=12");
        const recordings = await response.json();
        renderRecordings(recordings);
      } finally {
        refreshRecordingsButton.disabled = false;
      }
    }

    async function captureSnapshot() {
      snapshotButton.disabled = true;
      snapshotMessage.textContent = "Capturing HMI snapshot...";
      try {
        const response = await fetch("/api/snapshots", { method: "POST" });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Snapshot failed" }));
          throw new Error(error.detail || "Snapshot failed");
        }
        await refreshSnapshots();
        snapshotMessage.textContent = "Snapshot saved.";
      } catch (error) {
        snapshotMessage.textContent = error.message;
      } finally {
        snapshotButton.disabled = false;
      }
    }

    async function markManualFault(button) {
      button.disabled = true;
      try {
        const response = await fetch("/api/faults/manual", { method: "POST" });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Unable to mark fault" }));
          throw new Error(error.detail || "Unable to mark fault");
        }
        const eventsResponse = await fetch("/api/events");
        renderEvents(await eventsResponse.json());
      } catch (error) {
        status.className = "status";
        status.innerHTML = `<span class="dot"></span><span>${error.message}</span>`;
      } finally {
        button.disabled = false;
      }
    }

    async function captureBadPacks(button) {
      button.disabled = true;
      snapshotMessage.textContent = "Capturing bad pack camera snapshot...";
      try {
        const response = await fetch("/api/cameras/bad-packs", { method: "POST" });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Camera snapshot failed" }));
          throw new Error(error.detail || "Camera snapshot failed");
        }
        const snapshot = await response.json();
        const eventsResponse = await fetch("/api/events");
        renderEvents(await eventsResponse.json());
        snapshotMessage.textContent = `Bad pack snapshot saved: ${snapshot.filename}`;
      } catch (error) {
        snapshotMessage.textContent = error.message;
      } finally {
        button.disabled = false;
      }
    }

    async function captureCameraSnapshot() {
      const cameraId = activeCameras[0]?.id;
      if (!cameraId) {
        snapshotMessage.textContent = "No camera is configured.";
        return;
      }
      cameraSnapshotButton.disabled = true;
      snapshotMessage.textContent = `Capturing camera snapshot from ${cameraId}...`;
      try {
        const response = await fetch(`/api/cameras/${encodeURIComponent(cameraId)}/snapshots`, { method: "POST" });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Camera snapshot failed" }));
          throw new Error(error.detail || "Camera snapshot failed");
        }
        const snapshot = await response.json();
        const eventsResponse = await fetch("/api/events");
        renderEvents(await eventsResponse.json());
        snapshotMessage.textContent = `Camera snapshot saved: ${snapshot.filename}`;
      } catch (error) {
        snapshotMessage.textContent = error.message;
      } finally {
        cameraSnapshotButton.disabled = activeCameras.length === 0;
      }
    }

    function openShutdownModal() {
      shutdownModal.classList.add("open");
      confirmShutdown.focus();
    }

    function closeShutdownModal() {
      shutdownModal.classList.remove("open");
      shutdownButton.focus();
    }

    async function requestNodeShutdown() {
      confirmShutdown.disabled = true;
      confirmShutdown.textContent = "Shutting down...";
      try {
        const response = await fetch("/api/system/shutdown", { method: "POST" });
        if (!response.ok) {
          const error = await response.json().catch(() => ({ detail: "Shutdown request failed" }));
          throw new Error(error.detail || "Shutdown request failed");
        }
        snapshotMessage.textContent = "Shutdown requested. The node will go offline.";
        shutdownButton.disabled = true;
        closeShutdownModal();
      } catch (error) {
        snapshotMessage.textContent = error.message;
        confirmShutdown.disabled = false;
        confirmShutdown.textContent = "Yes, shut down node";
      }
    }

    async function refresh() {
      try {
        const [currentResponse, eventsResponse, configResponse, snapshotsResponse, camerasResponse, recordingsResponse] = await Promise.all([
          fetch("/api/current"),
          fetch("/api/events"),
          fetch("/api/config"),
          fetch("/api/snapshots"),
          fetch("/api/cameras"),
          fetch("/api/recordings?limit=12")
        ]);
        const current = await currentResponse.json();
        const events = await eventsResponse.json();
        const config = await configResponse.json();
        const snapshots = await snapshotsResponse.json();
        const cameras = await camerasResponse.json();
        const recordings = await recordingsResponse.json();
        renderCards(current.sample);
        renderStatus(current);
        renderSampleSummary(current.sample);
        renderEvents(events);
        renderHmi(config);
        renderSnapshots(snapshots);
        renderCameras(cameras);
        renderRecordings(recordings);
      } catch (error) {
        status.className = "status";
        status.innerHTML = `<span class="dot"></span><span>Dashboard error</span>`;
      }
    }

    snapshotButton.addEventListener("click", captureSnapshot);
    cameraSnapshotButton.addEventListener("click", captureCameraSnapshot);
    refreshRecordingsButton.addEventListener("click", refreshRecordings);
    shutdownButton.addEventListener("click", openShutdownModal);
    cancelShutdown.addEventListener("click", closeShutdownModal);
    shutdownModal.addEventListener("click", event => {
      if (event.target === shutdownModal) {
        closeShutdownModal();
      }
    });
    confirmShutdown.addEventListener("click", requestNodeShutdown);
    document.addEventListener("keydown", event => {
      if (event.key === "Escape" && shutdownModal.classList.contains("open")) {
        closeShutdownModal();
      }
    });
    viewMoreSnapshots.addEventListener("click", () => {
      showAllSnapshots = !showAllSnapshots;
      refreshSnapshots();
    });
    cards.addEventListener("click", event => {
      const manualFaultButton = event.target.closest("[data-action='mark-manual-fault']");
      if (manualFaultButton) {
        markManualFault(manualFaultButton);
        return;
      }

      const badPacksButton = event.target.closest("[data-action='capture-bad-packs']");
      if (badPacksButton) {
        captureBadPacks(badPacksButton);
      }
    });
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
