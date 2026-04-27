from collections.abc import Iterator
from contextlib import contextmanager

from pymodbus.client import ModbusTcpClient

from app.config import AppConfig, RegisterConfig


class MachineModbusClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self._client = ModbusTcpClient(config.machine_ip, port=config.machine_port)

    def connect(self) -> None:
        if not self._client.connect():
            raise ConnectionError(f"Could not connect to Modbus TCP at {self.config.machine_ip}:{self.config.machine_port}")

    def close(self) -> None:
        self._client.close()

    def read_registers(self) -> dict[str, int]:
        values: dict[str, int] = {}
        for register in self.config.registers:
            values[register.name] = self._read_single_register(register)
        return values

    def _read_single_register(self, register: RegisterConfig) -> int:
        response = self._client.read_holding_registers(register.address, count=1, slave=self.config.unit_id)
        if response.isError():
            raise RuntimeError(f"Modbus read failed for {register.name} at address {register.address}: {response}")
        return int(response.registers[0])


@contextmanager
def machine_client(config: AppConfig) -> Iterator[MachineModbusClient]:
    client = MachineModbusClient(config)
    client.connect()
    try:
        yield client
    finally:
        client.close()
