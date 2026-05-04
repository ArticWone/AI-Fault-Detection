# Vendor Documents

This page tracks vendor/OEM documents collected for the project so they can be found again without relying on external links.

## Smitec POSYC 3401/3402 Manual

- Local file: `downloads/smi_docs/Posyc 3401_3402 - Manual [105-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=1515911&chk=035CBBC71E0A4D921F23AF666EC2517E`
- Document title: `Industrial computers POSYC 3401/3402 - Installation, use and maintenance manual - EN`
- Version: `1.05`
- PDF metadata title: `DK400216-105-EN.book`
- PDF metadata creation date: `2024-11-05`
- Pages: `27`

Project relevance:

- Gives hardware context for the POSYC 3401/3402 industrial computer likely used as the machine HMI/controller interface.
- Documents power, grounding, panel-mount, USB, Ethernet, FLXIO, operating temperature, and maintenance guidance.
- Confirms POSYC 3401 has two `10/100 Mbps` Ethernet ports and isolated `24V` digital I/O.
- Confirms POSYC 3402 has one `10/100 Mbps` Ethernet port and no local I/O.
- Useful for HMI/network troubleshooting, but it is not a Modbus register map and does not define the BAR SAFETY logic.

Safety/use notes:

- Treat this as installation and hardware reference material only.
- Continue using read-only diagnostics unless OEM support explicitly authorizes deeper access.
- Do not modify machine control, safety circuits, or HMI internals based only on this manual.

## SICK 1040752 / IME12-04NPOZC0S Datasheet

- Local file: `downloads/sick_sensor_docs/SICK_1040752_IME12-04NPOZC0S_datasheet_en.pdf`
- Source URL: `https://www.sick.com/media/pdf/5/45/445/dataSheet_IME12-04NPOZC0S_1040752_en.pdf`
- Project note: `docs/sick-1040752-sensor.md`
- Document title: `IME IME12-04NPOZC0S, Data sheet`
- Subject: `Inductive proximity sensors`
- PDF metadata creation date: `2026-04-29`
- Pages: `7`

Project relevance:

- Documents the sensor recorded as SICK PN `1040752` for the B1/B2 replacement sensors.
- Confirms model `IME12-04NPOZC0S`, `M12 x 1`, `4 mm` sensing range, non-flush installation, `PNP NC` output, DC 3-wire wiring, and `M12` 4-pin connector.
- Useful for bracket alignment, target distance, wiring, and temperature checks during BAR SAFETY troubleshooting.

## Smitec FLXMOD DIO 16 Brochure

- Local file: `downloads/smi_docs/FlxMod DIO 16 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875515&chk=3AF6DCFFFF1E6FDE692F923842689BA0`
- Project note: `docs/smitec-flxmod-dio16-io-module.md`
- Document title/heading: `DIO 16 - Digital I/O module`
- PDF metadata creation date: `2024-11-13`
- Pages: `2`

Project relevance:

- Documents a Smitec FLXMOD digital I/O module with 16 software-configurable `24V` digital I/Os.
- Confirms `FLXIO` bus interface, DIN-rail mounting, `IP20`, IEC 61131-2 Type 1/Type 3 input characteristics, and current-sourcing high-side MOSFET outputs.
- Useful for understanding possible physical I/O hardware behind the B1/B2/B12/seal-bar safety signals.

## Smitec FLXMOD TCP A3 Brochure

- Local file: `downloads/smi_docs/FlxMod TCP A3 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875524&chk=47F9AF6C1132F2747ADDE46DCD40CE9C`
- Project note: `docs/smitec-flxmod-tcp-a3-thermocouple-module.md`
- Document title/heading: `TCP A3 - Thermocouples acquisition module`
- PDF metadata creation date: `2024-11-13`
- Pages: `2`

Project relevance:

- Documents a Smitec FLXMOD analog thermocouple acquisition module with three thermocouple inputs.
- Confirms `12 bit` resolution, insulated front-end circuitry, internal cold-junction compensation or optional external `LM335` sensor, and `FLXIO` bus interface.
- Useful for understanding possible physical analog/temperature hardware behind seal-bar temperature and heating values.

## Smitec FLXMOD PWR 02 Brochure

- Local file: `downloads/smi_docs/FlxMod PWR 02 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875526&chk=CCA8C39BE1445F8097271698F169ED6C`
- Project note: `docs/smitec-flxmod-pwr02-power-supply-module.md`
- Document title/heading: `PWR 02 - Power supply module`
- PDF metadata creation date: `2024-11-13`
- Pages: `2`

Project relevance:

- Documents a Smitec FLXMOD power supply module fed by `24 VDC`.
- Confirms backplane outputs of `24 VDC / 2 A max` auxiliary supply and `5 VDC / 3 A max` logic supply.
- Useful for understanding FLXMOD backplane power behind digital I/O and thermocouple modules.

## Smitec FLXMOD CVO A2 Brochure

- Local file: `downloads/smi_docs/FlxMod CVO A2 - Brochure [100-EN].pdf`
- Source URL: `https://smile.smigroup.it:4443/ords/dwld?id=875518&chk=D0CD85075E3C244A7AC89656DCF62EF6`
- Project note: `docs/smitec-flxmod-cvo-a2-analog-output-module.md`
- Document title/heading: `CVO A2 - Analog outputs module`
- PDF metadata creation date: `2024-11-13`
- Pages: `2`

Project relevance:

- Documents a Smitec FLXMOD analog output module with two software-configurable outputs.
- Confirms `0-10 V` or `4-20 mA` output ranges, `12 bit` resolution, insulated front-end circuitry, and `FLXIO` bus interface.
- Useful for understanding possible analog command hardware in the machine cabinet.

## SMIPACK BP802ALV 600R Use And Maintenance Manual

- Local file: `docs/vendor-documents/smipack/DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf`
- Drive title: `DM211643-S_B_EN (1).pdf`
- Manual code: `DM211643_S`
- Revision: `B`
- Machine: `BP802ALV 600R`
- BookStack page: `SMIPACK BP802ALV 600R Manual - Search Index`

Project relevance:

- Main machine manual for the automatic overlap shrinkwrapper with in-line infeed.
- Useful for tracing machine areas, safety devices, sealing bar faults, film faults, obstruction faults, and maintenance references.

## SMIPACK Industry 4.0 Ethernet And Modbus Manual

- Local file: `docs/vendor-documents/smipack/DM200289_D_Industry_4_0_Ethernet_Modbus.pdf`
- Drive title: `DM200289_D_Industry 4.0_EN (1).pdf`
- Manual code: `DM200289`
- Revision: `D2`
- BookStack page: `Industry 4.0 Ethernet and Modbus Settings`

Project relevance:

- Confirms Ethernet/VNC access flow for the HMI/operator panel.
- Documents key Modbus registers `13300`, `10142`, `10112`, and `10161`.
- Supports the node settings for machine IP `192.168.0.1`, Modbus TCP port `502`, and VNC port `5900`.

## SMIPACK External Reel-Holder Manual

- Local file: `docs/vendor-documents/smipack/DM200178_A_EN_external_reel_holder.pdf`
- Drive title: `DM200178_A_EN (1).pdf`
- Manual code: `DM200178`
- Revision: `A`
- BookStack page: `External Reel-Holder Settings and Sensors`

Project relevance:

- Documents the optional bottom-loading external reel-holder.
- Identifies reel-holder components, tensioning bar sensor, reel end photocell, and motor references including `50.SQ.4`, `51.B`, and `32.M.1`.

## SMIPACK Wiring Diagrams - Part 1 Scan

- Local file: `docs/vendor-documents/smipack/SMIPACK_wiring_diagrams_part_1_scan.pdf`
- Drive title: `[Untitled].pdf`
- Uploaded: `2026-05-04`
- Pages: `26`
- BookStack page: `Wiring Diagrams - Part 1 Scan Index`

Project relevance:

- First half of the electrical wiring diagrams.
- Useful for tracing sensors, terminal blocks, relays, contactors, safety circuits, and I/O modules into the machine parts and sensor map.
- This PDF is image-only, so searchable notes are maintained in BookStack until OCR is added.

## BookStack Searchable Library

The PDFs are imported into BookStack in two ways:

- As attachments on the matching summary pages in `Vendor Manuals and Machine Reference`.
- As extracted searchable text pages in the generated `Searchable PDF Library` chapter.

The wiring diagram scan is image-only. Its current library pages are sheet placeholders with searchable labels and trace tables; full diagram text will require OCR or manual trace notes.
