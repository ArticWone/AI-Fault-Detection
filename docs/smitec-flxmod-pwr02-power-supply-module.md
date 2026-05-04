# Smitec FLXMOD PWR 02 Power Supply Module

This note records the Smitec FLXMOD power supply module document added for project power/backplane reference.

## Identification

- Manufacturer: Smitec S.p.A.
- Product: `PWR 02`
- Description: FLXMOD system power supply module
- Local file: `downloads/smi_docs/FlxMod PWR 02 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875526&chk=CCA8C39BE1445F8097271698F169ED6C`
- Pages: `2`
- PDF metadata creator: `LibreOffice 24.2`
- PDF metadata creation date: `2024-11-13`

## Key Specs

- Input power supply: `24 VDC / 3 A max`
- Power outputs: two outputs delivered on the backplane
- Auxiliary supply output: `24 VDC / 2 A max`
- Logic supply output: `5 VDC / 3 A max`
- Protection features: overload and short-circuit protection on both outputs
- Bus termination resistor: absent
- FLXIO bus extension: RJ45 connector
- Housing: compact plastic case, polypropylene
- Degree of protection: `IP20`
- Mounting: standard DIN rail
- Operating temperature: `+5 C` to `+55 C`
- Storage temperature: `-25 C` to `+85 C`
- Relative humidity: `10%` to `95%`, non-condensing

## Project Relevance

- Useful context for FLXMOD coupler and I/O module power distribution.
- The module is fed by a `24 VDC` source and provides backplane supplies for the coupler and I/O modules stacked on the rail.
- Power quality, overloads, brownouts, or FLXIO backplane issues could affect digital I/O and analog temperature module behavior.
- The RJ45 connector is for FLXIO bus extension, not ordinary Ethernet unless OEM documentation confirms otherwise.

## Open Checks

- Confirm whether the machine cabinet uses this exact `PWR 02` module.
- Record module slot/location and any visible status indicators or wiring labels.
- Check 24V input, 24V auxiliary backplane output, and 5V logic output only using approved electrical safety procedures.
- Do not disconnect FLXIO bus or power wiring during machine operation.
