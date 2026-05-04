import os
from dataclasses import dataclass, field


def _default_data_root() -> str:
    if os.name == "nt":
        return "data"
    return os.environ.get("SMI_AI_DATA_ROOT", "/srv/smi-ai")


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    return float(value) if value else default


@dataclass(frozen=True)
class RegisterConfig:
    name: str
    address: int
    normal_min: int | None = None
    normal_max: int | None = None
    description: str = ""


@dataclass(frozen=True)
class AppConfig:
    machine_ip: str = field(default_factory=lambda: os.environ.get("SMI_MACHINE_IP", "192.168.0.1"))
    machine_port: int = field(default_factory=lambda: _env_int("SMI_MACHINE_PORT", 502))
    hmi_vnc_port: int = field(default_factory=lambda: _env_int("SMI_HMI_VNC_PORT", 5900))
    hmi_web_port: int = field(default_factory=lambda: _env_int("SMI_HMI_WEB_PORT", 6080))
    machine_connect_timeout: int = field(default_factory=lambda: _env_int("SMI_MACHINE_CONNECT_TIMEOUT", 120))
    poll_seconds: float = field(default_factory=lambda: _env_float("SMI_POLL_SECONDS", 2.0))
    unit_id: int = field(default_factory=lambda: _env_int("SMI_MODBUS_UNIT_ID", 1))
    event_log_path: str = field(
        default_factory=lambda: os.environ.get(
            "SMI_EVENT_LOG_PATH",
            os.path.join(_default_data_root(), "data", "events.csv"),
        )
    )
    registers: tuple[RegisterConfig, ...] = field(
        default_factory=lambda: (
            RegisterConfig("format", 13300, description="Current product format"),
            RegisterConfig("set_format", 10142, description="Requested product format"),
            RegisterConfig("lot_number", 10112, description="Active lot number"),
            RegisterConfig("package_count", 10161, normal_min=0, description="Package counter"),
        )
    )


DEFAULT_CONFIG = AppConfig()
