# Wiring Diagrams - Part 1 Scan Index

Source PDF: `docs/vendor-documents/smipack/SMIPACK_wiring_diagrams_part_1_scan.pdf`

Drive title: `[Untitled].pdf`

Uploaded: `2026-05-04`

Status: Part 1 of the wiring diagrams. Part 2 is expected after the next scan.

## Purpose

This page makes the first scanned wiring diagram packet searchable in BookStack and gives us a place to record traced wires, sensors, terminals, pages, and cabinet references.

The PDF is an image scan, so text search inside the PDF may be limited until OCR is added.

## Search Terms

- wiring diagram
- electrical drawing
- schematic
- cabinet
- terminal
- terminal block
- wire number
- sensor cable
- I/O module
- FLXIO
- FLXMOD
- DIO 16
- TCP A3
- relay
- contactor
- safety relay
- emergency stop
- door interlock
- sealing bar
- B1
- B2
- B11
- B12
- SQ13
- 50.SQ.4
- 50.SQ.5
- 51.B
- 52.SQ.4
- 52.SQ.5
- 55.SQ.2
- 162.KM.8
- 162.KM.9
- 60.KA.3
- 32.M.1

## Trace Table

| Page/sheet | Wire/terminal | Device label | Device type | Machine area | Related register/fault | Status |
| --- | --- | --- | --- | --- | --- | --- |
| unknown | unknown | unknown | unknown | unknown | unknown | needs trace |

## Mapping Workflow

1. Identify each sheet/page number from the scan.
2. Record visible device labels such as `B12`, `SQ13`, `KM`, `KA`, `M`, and terminal numbers.
3. Match labels to the machine parts and sensor map.
4. Confirm with read-only Modbus values, HMI alarms, or camera evidence.
5. Mark each row as `candidate`, `verified`, or `retired`.

## Known Next Step

Add wiring diagrams part 2 after it is scanned on `2026-05-05`, then merge both packets into one trace index.
