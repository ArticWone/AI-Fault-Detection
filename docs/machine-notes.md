# Machine Notes

## Connection
- Ethernet port on HMI or inside cabinet
- IP configured via Utility -> Network

## VNC Access
- Use UltraVNC Viewer
- IP: stored locally, do not publish
- Password: stored locally, do not publish

## Known Registers
- 13300: format
- 10142: set format
- 10112: lot number
- 10161: package count

## Candidate Registers From 2026-04-27 Testing
See `docs/findings-2026-04-27.md` for evidence and log references.

- 10059: machine state / START-STOP candidate
- 10167: E-stop/run-state standout or process value
- 10168: B2 candidate
- 10182: B2 candidate
- 10183: top film-feed candidate
- 10189: pulse or enable candidate
- 10209: fault-window candidate
- 10217: state code candidate
- 10231: state/sensor-group candidate
- 13445: B12 candidate
- 13505: B12 candidate

## Goal
Identify fault registers by comparing values during faults.
