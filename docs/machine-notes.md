# Machine Notes

## Connection
- Ethernet port on HMI or inside cabinet
- IP configured via Utility -> Network

## VNC Access
- Use UltraVNC Viewer
- IP: stored locally, do not publish
- Password: stored locally, do not publish

## HMI / Industrial Computer Reference
- Downloaded vendor document: `downloads/smi_docs/Posyc 3401_3402 - Manual [105-EN].pdf`
- Project index note: `docs/vendor-documents.md`
- The manual covers Smitec POSYC 3401/3402 installation, hardware, Ethernet, USB, FLXIO, power, grounding, operating temperature, and maintenance.
- It is useful for HMI/network hardware context, but it does not provide a Modbus register map or BAR SAFETY logic definition.

## B1/B2 Sensor Reference
- Recorded replacement sensor: SICK PN `1040752`, model `IME12-04NPOZC0S`.
- Project sensor note: `docs/sick-1040752-sensor.md`
- Local datasheet: `downloads/sick_sensor_docs/SICK_1040752_IME12-04NPOZC0S_datasheet_en.pdf`
- Important traits: inductive proximity sensor, `M12 x 1`, `4 mm` nominal range, non-flush mount, DC 3-wire, `PNP NC`, male `M12` 4-pin connector, `IP67`.
- Troubleshooting implication: bracket angle, target distance/material, vibration, cable strain, and the normally closed PNP output behavior can all affect BAR SAFETY interpretation.

## I/O Module Reference
- Downloaded vendor document: `downloads/smi_docs/FlxMod DIO 16 - Brochure [100-EN].pdf`
- Project I/O note: `docs/smitec-flxmod-dio16-io-module.md`
- The document covers the Smitec FLXMOD `DIO 16` digital I/O module.
- Important traits: 16 software-configurable `24V` digital I/Os, `FLXIO` bus, DIN-rail mount, IEC 61131-2 Type 1/Type 3 inputs, high-side MOSFET outputs, `500 mA` max output current.
- Troubleshooting implication: physical B1/B2/B12/seal-bar safety inputs may be packed or encoded through FLXIO I/O hardware before appearing in Modbus.

## Analog Thermocouple Module Reference
- Downloaded vendor document: `downloads/smi_docs/FlxMod TCP A3 - Brochure [100-EN].pdf`
- Project thermocouple note: `docs/smitec-flxmod-tcp-a3-thermocouple-module.md`
- The document covers the Smitec FLXMOD `TCP A3` thermocouple acquisition module.
- Important traits: three thermocouple inputs, `12 bit` resolution, insulated front-end, internal cold-junction compensation or optional external `LM335`, `FLXIO` bus.
- Troubleshooting implication: seal-bar/oven temperature values may pass through FLXIO analog hardware before appearing in HMI history or Modbus-readable values.

## FLXMOD Power Supply Reference
- Downloaded vendor document: `downloads/smi_docs/FlxMod PWR 02 - Brochure [100-EN].pdf`
- Project power note: `docs/smitec-flxmod-pwr02-power-supply-module.md`
- The document covers the Smitec FLXMOD `PWR 02` power supply module.
- Important traits: `24 VDC / 3 A max` input, backplane `24 VDC / 2 A max` auxiliary output, backplane `5 VDC / 3 A max` logic output, overload/short-circuit protection, FLXIO bus extension by RJ45.
- Troubleshooting implication: unstable FLXMOD power/backplane behavior could affect digital I/O and analog thermocouple readings.

## Analog Output Module Reference
- Downloaded vendor document: `downloads/smi_docs/FlxMod CVO A2 - Brochure [100-EN].pdf`
- Project analog output note: `docs/smitec-flxmod-cvo-a2-analog-output-module.md`
- The document covers the Smitec FLXMOD `CVO A2` analog outputs module.
- Important traits: two software-configurable analog outputs, `0-10 V` or `4-20 mA`, `12 bit` resolution, insulated front-end, `FLXIO` bus, `24 VDC / 1.5 A max` I/O supply for external loads.
- Troubleshooting implication: if installed, analog commands may be represented in HMI/Modbus as software output values rather than raw terminal measurements.

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
