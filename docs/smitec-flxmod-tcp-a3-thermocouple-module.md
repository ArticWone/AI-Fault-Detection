# Smitec FLXMOD TCP A3 Thermocouple Module

This note records the Smitec analog thermocouple acquisition module document added for project temperature/I-O reference.

## Identification

- Manufacturer: Smitec S.p.A.
- Product: `TCP A3`
- Description: FLXMOD system thermocouples acquisition module
- Local file: `downloads/smi_docs/FlxMod TCP A3 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875524&chk=47F9AF6C1132F2747ADDE46DCD40CE9C`
- Pages: `2`
- PDF metadata creator: `LibreOffice 24.2`
- PDF metadata creation date: `2024-11-13`

## Key Specs

- Analog input count: `3`
- Analog input type: thermocouples
- Input resolution: `12 bit`
- Front-end: insulated front-end circuitry
- Cold-junction compensation: internal, or external with optional `LM335` sensor
- Internal cold-junction compensation range: `-50.3 C` to `+99.7 C`
- Analog input range: `-2.582 mV` to `+28.405 mV`
- J-type thermocouple range: `-53.24 C` to `+518.04 C`
- K-type thermocouple range: `-69.85 C` to `+682.74 C`
- Housing: compact plastic case, polypropylene
- Degree of protection: `IP20`
- Mounting: standard DIN rail
- Interface: proprietary `FLXIO`
- Bus address setting: rotary switch
- Logic supply: `24 VDC` and `5 VDC` from backplane
- Operating temperature: `+5 C` to `+55 C`
- Storage temperature: `-25 C` to `+85 C`
- Relative humidity: `10%` to `95%`, non-condensing

## Project Relevance

- Useful context for seal-bar temperature and oven/heating related machine values.
- The HMI export already shows seal-bar temperature changes under data ID `13600`.
- If the cabinet uses this module, temperature values may pass through FLXIO analog hardware before being represented in HMI parameters or Modbus-readable values.
- Cold-junction compensation and thermocouple type matter when comparing actual temperature, HMI temperature, and any diagnostic values.

## Open Checks

- Confirm whether the machine cabinet uses this exact `TCP A3` module.
- Record module slot/location, rotary address, and channel labels if visible in the cabinet.
- Confirm whether the seal-bar thermocouple is J-type or K-type.
- Confirm whether cold-junction compensation is internal or external with an `LM335` sensor.
- Compare HMI seal-bar temperature to a trusted external measurement before drawing conclusions about sensor or module accuracy.
