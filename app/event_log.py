import csv
from pathlib import Path

from app.detector import FaultEvent


FIELDNAMES = ("timestamp", "severity", "source", "message", "recommendation")


class EventLogger:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
                writer.writeheader()

    def write(self, event: FaultEvent) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writerow(
                {
                    "timestamp": event.timestamp.isoformat(timespec="seconds"),
                    "severity": event.severity,
                    "source": event.source,
                    "message": event.message,
                    "recommendation": event.recommendation,
                }
            )
