# Modbus Reference Notes

## Useful Documentation

Official Modbus documentation:
- Modbus specifications and implementation guides: https://www.modbus.org/modbus-specifications
- Modbus Application Protocol Specification V1.1b3: https://www.modbus.org/file/secure/modbusprotocolspecification.pdf

Python library documentation:
- PyModbus reading registers: https://www.pymodbus.org/docs/reading-registers
- PyModbus basic concepts: https://www.pymodbus.org/docs/basic-concepts
- PyModbus function codes: https://www.pymodbus.org/docs/function-codes
- PyModbus data types: https://www.pymodbus.org/docs/data-types

SMIPACK machine documentation found publicly:
- Related SMIPACK BP802AR 340P / BP800AR 340P use and maintenance manual: https://www.manualslib.com/manual/3912359/Smipack-Bp802ar-340p.html

No public SMIPACK BP802ALV Modbus register map was found during the first web search. Treat the register map in this project as field-discovered until a vendor document is obtained.

## Modbus Basics For This Project

The SMIPACK machine is being read over Modbus TCP on port `502`.

The current code uses holding-register reads:
- function code `03`
- PyModbus method: `read_holding_registers`
- default unit/device id: `1`

Modbus registers are 16-bit words. Multi-register values may need decoding as 32-bit integers, floats, signed values, or bitfields. Do not assume every register is a simple unsigned integer until it is validated against machine behavior.

## Addressing Warning

Modbus documentation often shows holding registers as `40001`, `40002`, etc. Many libraries, including PyModbus, use zero-based protocol addresses.

Example:
- vendor notation `40001`
- protocol/PyModbus address `0`

The SMIPACK addresses already discovered in this project, such as `10161` and `10209`, appear to be raw addresses used directly with PyModbus. Keep this convention consistent unless vendor documentation proves otherwise.

## Read-Only Safety Rule

Use read-only operations while mapping the machine:
- safe starting point: `read_holding_registers`
- avoid write operations: `write_register`, `write_registers`, `write_coil`, `write_coils`

This project must not directly control emergency stop or other safety systems.

## Practical Mapping Workflow

1. Confirm connection to `192.168.0.1:502`.
2. Read known stable registers first.
3. Capture baseline values while the machine is idle.
4. Add operator markers for physical events.
5. Compare before/during/after values for each action.
6. Promote only repeatable findings into the register map.
7. Add detector rules only after each mapping is confirmed across multiple runs.

Useful known registers from project notes:
- `13300`: format
- `10142`: set format
- `10112`: lot number
- `10161`: package count

High-value candidate registers:
- `10059`: machine state / START-STOP candidate
- `10167`: E-stop/run-state standout or process value
- `10168`: B2 candidate
- `10182`: B2 candidate
- `10183`: top film-feed candidate
- `10209`: fault-window candidate
- `10217`: state code candidate
- `10231`: state/sensor-group candidate
- `13445`: B12 candidate
- `13505`: B12 candidate
