# Machine Connection and Modbus

## Endpoint

- Machine/HMI IP: `192.168.0.1`
- Modbus TCP port: `502`
- VNC port: `5900`
- Default Modbus unit id: `1`

## Known Registers

| Register | Meaning |
| --- | --- |
| `13300` | Current format |
| `10142` | Set/requested format |
| `10112` | Lot number |
| `10161` | Package count |

## High-Value Candidates

| Register | Candidate meaning |
| --- | --- |
| `10059` | Machine state / start-stop candidate |
| `10167` | E-stop/run-state standout or process value |
| `10168`, `10182` | B1/B2 or B2 group candidates |
| `10183` | Top film-feed candidate |
| `10209` | Fault-window candidate |
| `10217`, `10231` | State/sensor group candidates |
| `13445`, `13505` | B12 direct candidates |
| `10325`, `13539` | Seal-bar or B12 secondary candidates |

## Read-Only Rule

Use holding-register reads only while mapping. Do not write coils/registers or command machine motion.

```bash
mbpoll -m tcp -a 1 -r 10112 -c 4 192.168.0.1
```
