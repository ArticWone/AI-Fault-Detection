# SMIPACK BP802ALV 600R Manual - Search Index

Source PDF: `docs/vendor-documents/smipack/DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf`

Manual code: `DM211643_S`

Machine: `BP802ALV 600R`

Description: Automatic overlap shrinkwrapper with in-line infeed.

## High-Value Search Terms

- BP802ALV 600R
- automatic overlap shrinkwrapper
- in-line infeed
- sealing bar
- film reel
- upper unwinder
- lower unwinder
- chain separator
- oven belt
- emergency door open
- bar safety
- film finishing
- film finished
- no pressure
- oven obstruction
- B11 obstruction
- B12 obstruction
- SQ13 problem
- inverter error
- I/O bus error

## Machine Areas To Map

| Area | Manual reference | Map use |
| --- | --- | --- |
| Infeed belt | Machine components and setup | Product entry and flow detection |
| Chain separator | Operation, alarms, inverter references | Pack spacing and obstruction faults |
| Sealing bar | Safety devices, maintenance, bar movement faults | Seal cycle, bar safety, sensor mapping |
| Film reels and unwinders | Film setup and film alarms | Film feed, reel end, tensioning |
| Oven / thermal chamber | Operation and temperature faults | Heat shrink, oven belt, PT100/temperature checks |
| Operator panel | Operation and alarms | HMI state, VNC view, operator prompts |

## Safety Devices And Sensors Mentioned

- Door magnetic sensors.
- Sealing bar sensors.
- Emergency mushroom button.
- Safety relay circuits.
- Tensioning bar sensors.
- Outfeed accumulation photocell.
- Obstruction photocell.
- Pressure switch.
- Oven temperature probe.
- Inverter/driver status signals.

## Alarm/Fault Phrases To Correlate

| Alarm phrase | Useful mapping target |
| --- | --- |
| `EMERGENCY DOOR OPEN` | Door interlocks and safety relay |
| `BAR SAFETY` | Sealing bar safety sensors and obstruction area |
| `FILM FINISHING` | Reel-end monitoring and film reserve |
| `FILM FINISHED` | Tensioning bar and reel-end sensors |
| `BAR MOVEMENT PROBLEM` | Bar position sensors, air pressure, solenoid valves |
| `OVEN OBSTRUCTION` | Outfeed/oven photocell timing |
| `CHAIN SEPARATOR OBSTRUCTION` | B11 sensor and chain separator path |
| `B12 OBSTRUCTION` | Sensor B12 near sealing bar |
| `NO PRESSURE` | Pneumatic supply and pressure switch |
| `ERROR I/O BUS 0` / `ERROR I/O BUS 1` | FLXIO module communication |

## Mapping Notes

Use this manual while filling in the machine parts and sensor map. Treat every physical sensor row as `candidate` until verified by both physical tracing and read-only data changes.
