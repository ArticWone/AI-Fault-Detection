"""Quick raw Modbus probe.

Use app/main.py for the normal fault-detection workflow.
"""

from pymodbus.client import ModbusTcpClient


def main() -> None:
    client = ModbusTcpClient("192.168.0.1")
    client.connect()

    result = client.read_holding_registers(10000, count=50, slave=1)
    print(result.registers)

    client.close()


if __name__ == "__main__":
    main()
