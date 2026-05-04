# Start Here

The SMI AI node is a monitoring and documentation system for the SMIPACK BP802ALV machine area. It provides a shop-floor Web UI, camera preview/recording, machine Modbus monitoring, HMI viewing, BookStack documentation, and a path toward AI-assisted fault detection.

## Safety Boundary

- The node is read-only toward the machine during diagnostics.
- It must not control emergency stop, bypass safety, or command motion.
- Operator buttons in the Web UI record events and snapshots; they do not control the machine.

## Primary URLs

| Purpose | URL |
| --- | --- |
| SMI Web UI | `http://192.168.0.20/` or `http://192.168.0.20:8000/` |
| BookStack | `http://192.168.0.20:6875/` |
| Camera Admin | `http://192.168.0.25/` |
| go2rtc | `http://192.168.0.20:1984/` |

## Current Priorities

1. Connect machine at `192.168.0.1` and confirm Modbus TCP on port `502`.
2. Continue documenting BAR SAFETY and bad-pack evidence.
3. Use the Reolink camera and snapshots to correlate visible behavior with Modbus/HMI events.
4. Keep BookStack as the living manual for machine settings, network, services, and troubleshooting.
