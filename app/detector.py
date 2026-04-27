from dataclasses import dataclass
from datetime import datetime

from app.config import RegisterConfig


@dataclass(frozen=True)
class FaultEvent:
    timestamp: datetime
    severity: str
    source: str
    message: str
    recommendation: str


class BasicFaultDetector:
    """Rule-based starting point that can later be replaced or assisted by ML."""

    def __init__(self, registers: tuple[RegisterConfig, ...]):
        self._registers = {register.name: register for register in registers}
        self._previous_values: dict[str, int] = {}

    def inspect(self, values: dict[str, int]) -> list[FaultEvent]:
        events: list[FaultEvent] = []
        now = datetime.now()

        for name, value in values.items():
            register = self._registers.get(name)
            if register is None:
                continue

            if register.normal_min is not None and value < register.normal_min:
                events.append(
                    FaultEvent(
                        now,
                        "warning",
                        name,
                        f"{name} is below expected range: {value}",
                        "Verify the register mapping and inspect the machine state.",
                    )
                )

            if register.normal_max is not None and value > register.normal_max:
                events.append(
                    FaultEvent(
                        now,
                        "warning",
                        name,
                        f"{name} is above expected range: {value}",
                        "Check for a stuck sensor, incorrect format, or register scaling issue.",
                    )
                )

        if self._previous_values:
            events.extend(self._detect_counter_stall(values, now))

        self._previous_values = values.copy()
        return events

    def _detect_counter_stall(self, values: dict[str, int], now: datetime) -> list[FaultEvent]:
        package_count = values.get("package_count")
        previous_count = self._previous_values.get("package_count")

        if package_count is None or previous_count is None:
            return []

        if package_count < previous_count:
            return [
                FaultEvent(
                    now,
                    "info",
                    "package_count",
                    f"Package count reset from {previous_count} to {package_count}",
                    "Confirm this was caused by a lot change or operator reset.",
                )
            ]

        return []
