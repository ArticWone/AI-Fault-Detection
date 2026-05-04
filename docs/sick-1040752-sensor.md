# SICK 1040752 Sensor Reference

This note records the currently identified B1/B2 replacement sensor used in the project.

## Identification

- Manufacturer: SICK
- Part number: `1040752`
- Type/model: `IME12-04NPOZC0S`
- Product family: `IME`
- Sensor type: inductive proximity sensor
- Local datasheet: `downloads/sick_sensor_docs/SICK_1040752_IME12-04NPOZC0S_datasheet_en.pdf`
- SICK datasheet source: `https://www.sick.com/media/pdf/5/45/445/dataSheet_IME12-04NPOZC0S_1040752_en.pdf`

## Key Specs

- Housing: standard cylindrical/threaded design
- Thread size: `M12 x 1`
- Diameter: `12 mm`
- Sensing range `Sn`: `4 mm`
- Safe sensing range `Sa`: `3.24 mm`
- Installation type: non-flush
- Switching frequency: `2,000 Hz`
- Connection: male `M12`, `4-pin`
- Electrical wiring: DC 3-wire
- Supply voltage: `10 VDC` to `30 VDC`
- Switching output: `PNP`
- Output function: `NC` / normally closed
- Continuous current `Ia`: `200 mA`
- Enclosure rating: `IP67`
- Ambient operating temperature: `-25 C` to `+75 C`
- Housing material: nickel-plated brass
- Sensing face material: plastic, PA 66
- Housing length: `65 mm`
- Thread length: `43 mm`
- Max tightening torque: `12 Nm`
- Items supplied: two nickel-plated brass mounting nuts

## Connection Notes

Datasheet connection diagram: `Cd-008`.

- Pin `1`, brown `BN`: `+ (L+)`
- Pin `3`, blue `BU`: `- (M)`
- Pin `4`, black `BK`: `NC` output
- Pin `2`, white `WH`: not connected

## Material Reduction Factors

The sensor response depends on target material. SICK lists these as reference values:

- St37 steel: `1.0`
- Stainless steel V2A / 304: approx. `0.8`
- Aluminum: approx. `0.45`
- Copper: approx. `0.4`
- Brass: approx. `0.4`

## Project Relevance

- The project status notes record SICK PN `1040752` as the replacement part for the B1/B2 sensors.
- The `PNP NC` behavior matters when interpreting signal drops: a target/sequence issue may appear as a normally closed output changing state, depending on the PLC input wiring and controller logic.
- Because this is a non-flush inductive sensor with a `4 mm` nominal sensing range and `3.24 mm` safe sensing range, bracket angle, sensor depth, target material, and vibration can all affect repeatability.
- The `-25 C` to `+75 C` ambient rating is useful for warmup/fault correlation, but local heat near the seal bar, cable strain, and bracket movement should still be checked under real running conditions.

## Open Checks

- Confirm the physical label on the installed B1/B2 sensors reads `IME12-04NPOZC0S` or SICK `1040752`.
- Confirm whether both B1 and B2 use the exact same part number.
- Confirm target material and actual measured sensor-to-target distance.
- Confirm the installed M12 cable pinout and whether pin `2` is unused in the machine harness.
- Compare live signal behavior with the normally closed PNP expectation before drawing conclusions from Modbus values.
