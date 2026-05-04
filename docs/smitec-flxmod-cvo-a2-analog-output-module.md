# Smitec FLXMOD CVO A2 Analog Output Module

This note records the Smitec analog output module document added for project analog I/O reference.

## Identification

- Manufacturer: Smitec S.p.A.
- Product: `CVO A2`
- Description: FLXMOD system analog outputs module
- Local file: `downloads/smi_docs/FlxMod CVO A2 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875518&chk=D0CD85075E3C244A7AC89656DCF62EF6`
- Pages: `2`
- PDF metadata creator: `LibreOffice 24.2`
- PDF metadata creation date: `2024-11-13`

## Key Specs

- Analog output count: `2`
- Analog output ranges: `0-10 V` or `4-20 mA`
- Output range configuration: software configurable
- Output resolution: `12 bit`
- Front-end: insulated front-end circuitry
- Housing: compact plastic case, polypropylene
- Degree of protection: `IP20`
- Mounting: standard DIN rail
- Interface: proprietary `FLXIO`
- Bus address setting: rotary switch
- I/O supply: `24 VDC / 1.5 A max` for external loads
- Logic supply: `24 VDC` and `5 VDC` from backplane
- Operating temperature: `+5 C` to `+55 C`
- Storage temperature: `-25 C` to `+85 C`
- Relative humidity: `10%` to `95%`, non-condensing

## Project Relevance

- Useful context for analog control signals that may drive external devices through `0-10 V` or `4-20 mA` outputs.
- If installed, this module could relate to analog command values for machine subsystems such as drives, controls, or proportional devices.
- The module communicates over `FLXIO`, so HMI/Modbus values may represent software-level output commands rather than raw terminals directly.

## Open Checks

- Confirm whether the machine cabinet uses this exact `CVO A2` module.
- Record module slot/location, rotary address, and channel labels if visible in the cabinet.
- Identify whether each channel is configured for `0-10 V` or `4-20 mA`.
- Do not force analog outputs or change output configuration without OEM authorization.
