# Smitec FLXMOD DIO 16 I/O Module

This note records the Smitec digital I/O module document added for project I/O reference.

## Identification

- Manufacturer: Smitec S.p.A.
- Product: `DIO 16`
- Description: FLXMOD system digital I/O module
- Local file: `downloads/smi_docs/FlxMod DIO 16 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875515&chk=3AF6DCFFFF1E6FDE692F923842689BA0`
- Pages: `2`
- PDF metadata creator: `LibreOffice 24.2`
- PDF metadata creation date: `2024-11-13`

## Key Specs

- Digital I/O count: `16`
- I/O type: software-configurable digital `24V` I/Os
- Mounting: standard DIN rail
- Housing: compact plastic case, polypropylene
- Degree of protection: `IP20`
- Input characteristics: Type 1 and Type 3 according to `IEC 61131-2`
- Output characteristics: current-sourcing high-side MOSFET outputs with fast demagnetizing feature
- Max output current: `500 mA`
- Protection features: overload, short-circuit, and overtemperature
- Interface: proprietary `FLXIO`
- Bus address setting: rotary switch
- I/O supply: `24 VDC / 7 A max`
- Logic supply: `24 VDC` and `5 VDC` from backplane
- Operating temperature: `+5 C` to `+55 C`
- Storage temperature: `-25 C` to `+85 C`
- Relative humidity: `10%` to `95%`, non-condensing

## Project Relevance

- Useful context for tracing machine digital inputs/outputs related to B1, B2, B12, seal-bar position, and BAR SAFETY behavior.
- Confirms that the module is intended for industrial `24V` sensors and actuators and communicates with the CPU over Smitec's proprietary `FLXIO` bus.
- Helps explain why project Modbus registers may expose packed or encoded I/O state rather than one plain register per sensor.

## Open Checks

- Confirm whether the machine cabinet uses this exact `DIO 16` module.
- Record module slot/location, rotary address, and terminal labels if visible in the cabinet.
- Match physical B1/B2/B12 wiring to the actual I/O module/channel before treating any Modbus candidate as confirmed.
- Continue using read-only diagnostics; do not force outputs or bypass safety circuits.
