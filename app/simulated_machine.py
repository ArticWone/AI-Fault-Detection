from itertools import count


class SimulatedMachine:
    """Predictable local data source for building without the real machine attached."""

    def __init__(self) -> None:
        self._ticks = count(1)
        self._package_count = 0

    def read_registers(self) -> dict[str, int]:
        tick = next(self._ticks)
        self._package_count += 1

        if tick % 20 == 0:
            self._package_count = 0

        return {
            "format": 1,
            "set_format": 1,
            "lot_number": 1001,
            "package_count": self._package_count,
        }
