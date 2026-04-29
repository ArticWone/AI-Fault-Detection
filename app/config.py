from dataclasses import dataclass, field


@dataclass(frozen=True)
class RegisterConfig:
    name: str
    address: int
    normal_min: int | None = None
    normal_max: int | None = None
    description: str = ""


@dataclass(frozen=True)
class AppConfig:
    machine_ip: str = "192.168.0.1"
    machine_port: int = 502
    hmi_vnc_port: int = 5900
    hmi_web_port: int = 6080
    poll_seconds: float = 2.0
    unit_id: int = 1
    event_log_path: str = "data/events.csv"
    registers: tuple[RegisterConfig, ...] = field(
        default_factory=lambda: (
            RegisterConfig("format", 13300, description="Current product format"),
            RegisterConfig("set_format", 10142, description="Requested product format"),
            RegisterConfig("lot_number", 10112, description="Active lot number"),
            RegisterConfig("package_count", 10161, normal_min=0, description="Package counter"),
        )
    )


DEFAULT_CONFIG = AppConfig()
