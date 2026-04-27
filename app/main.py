import argparse
import time

from app.config import DEFAULT_CONFIG
from app.detector import BasicFaultDetector
from app.event_log import EventLogger
from app.modbus_client import machine_client
from app.simulated_machine import SimulatedMachine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Basic AI fault detection proof of concept")
    parser.add_argument("--simulate", action="store_true", help="Use generated machine data instead of Modbus TCP")
    parser.add_argument("--once", action="store_true", help="Read one sample and exit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = DEFAULT_CONFIG
    detector = BasicFaultDetector(config.registers)
    logger = EventLogger(config.event_log_path)

    if args.simulate:
        machine = SimulatedMachine()
        run_loop(machine, detector, logger, config.poll_seconds, args.once)
        return

    with machine_client(config) as machine:
        run_loop(machine, detector, logger, config.poll_seconds, args.once)


def run_loop(machine, detector: BasicFaultDetector, logger: EventLogger, poll_seconds: float, once: bool) -> None:
    while True:
        values = machine.read_registers()
        print(f"Machine values: {values}")

        events = detector.inspect(values)
        for event in events:
            logger.write(event)
            print(f"[{event.severity.upper()}] {event.message} Recommendation: {event.recommendation}")

        if once:
            break

        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
