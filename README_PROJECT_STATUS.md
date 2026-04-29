# SMI AI Fault Detection - Project Status

This project is a non-invasive diagnostic effort for recurring SMI BP802ALV production faults during 10 oz bottle operation. The intent is to document what has been observed, what has been tested, what data has been captured, and what support questions remain open. This is not written to assign blame to the OEM or any technician. It is a factual working record so the next troubleshooting step starts from the full context.

## Current Summary

- Machine: SMI / SMIPACK BP802ALV.
- Active production issue: recurring seal bar / BAR SAFETY related stops and bad packs after changeover from 20 oz bottles to 10 oz bottles.
- Diagnostic approach: read-only observation using HMI alarm/state exports, Modbus TCP logging, operator markers, VNC/HMI screenshots, photos, video, and controlled physical sensor tests.
- Safety boundary: the diagnostic tooling does not write machine values, command motion, bypass safety, or defeat any safety circuit.
- Current focus: BAR SAFETY / B1-B2 / B12 / seal-bar safety sequence.
- Current status: field diagnostics strongly narrow the issue to the safety/sensor sequence, but a single root cause has not been proven.

## Working Theory

The current evidence points toward instability or timing mismatch in the B1/B2/B12/seal-bar safety sequence rather than a simple single failed sensor.

Likely contributing areas still under review:

- B1/B2 paired timing or alignment.
- B12 state interaction with seal-bar movement.
- Seal-bar position feedback and safety interpretation.
- Sensor mounting or mechanical variation during operation.
- Heat, vibration, cable strain, connector movement, or electrical noise.
- Controller logic interpretation of the expected sensor sequence.

This theory is based on correlation, not a final root-cause conclusion.

## Important Known Facts

- B1 and B2 were clarified by the technician as a tied pair, with B2 acting as the slave.
- B2 could not be bypassed by unplugging; unplugging caused the machine to fault.
- B1/B2 sensors have been replaced. The recorded part number is SICK PN `1040752`.
- The B2 bracket was found not to be a true 90-degree bend and was corrected.
- Correcting the bracket reduced fault frequency but did not eliminate the fault.
- Film/inverter tuning changes affected behavior but did not resolve the fault.
- The HMI alarm history repeatedly shows BAR SAFETY events paired with machine stop transitions.
- Read-only Modbus logging can correlate fault windows with B1/B2, B12, and seal-bar candidate registers.
- We have not isolated one single Modbus bit that exactly equals "BAR SAFETY active."

## Timeline By Day

### 2026-04-27 - Initial Access, Logging, and First Fault Capture

Work completed:

- Established direct Ethernet access to the machine.
- Confirmed machine services:
  - Modbus TCP on port `502`.
  - VNC on port `5900`.
  - SSH visible on port `22`, but not used for diagnostics without OEM authorization.
- Set up Python tooling with `pymodbus`.
- Built read-only logging tools:
  - Cold-start logger.
  - Broad live-output logger.
  - Candidate sensor logger.
  - Operator marker script.
- Captured first clean cold-start and live Modbus logs.
- Logged an observed production fault during package processing.

Important 2026-04-27 fault markers:

- `FAULT_CYCLE_START` at `2026-04-27T14:08:05.039-05:00`.
- `CHECKPOINT_2_PACKS_OK` at `2026-04-27T14:10:08.077-05:00`.
- `FAULT_OBSERVED` at `2026-04-27T14:11:34.615-05:00`.

Early fault-window candidates:

- `10190`
- `10208`
- `10209`
- `10167`
- `10168`
- `10182`
- `10217`
- `10231`

Notable observation:

- Register `10209` repeatedly flipped between `0` and `65535` before the observed fault.
- Registers `10190` and `10208` showed large changes near the fault window.

Reference files:

- `docs/findings-2026-04-27.md`
- `data/live_outputs/20260427/135809/`
- `data/candidate_sensor_runs/20260427_152831/`

### 2026-04-28 - Sensor Mapping, HMI Review, and Mechanical/Tuning Work

Work completed:

- Continued live Modbus logging and operator marker use.
- Used controlled physical tests to map sensor/control behavior to Modbus candidates.
- Captured HMI screenshots and relevant HMI parameter pages.
- Reviewed machine behavior during failures and began narrowing from broad "seal bar error" to the B1/B2/B12/seal-bar safety sequence.
- Recorded technician clarification that B1/B2 are tied and B2 is the slave.

Physical mapping results:

- B1/B2 tied pair or B2 group:
  - `10168`
  - `10182`
- B12 direct candidates:
  - `13445`
  - `13505`
- Seal-bar or B12 secondary candidates:
  - `10325`
  - `13539`
- Machine stopped/running:
  - `10059`
- Running enable/value:
  - `10189`
- Top film-feed sensor:
  - `10183`

Mechanical and tuning steps:

- Film slack/motion adjustments were attempted using inverter acceleration and deceleration values.
- Lowering acceleration from `2000 Hz/s` to `1800 Hz/s` made the issue worse.
- Raising acceleration to `2200 Hz/s` was reported as slightly better but did not resolve the fault.
- Deceleration tests at `900 Hz/s` and `1200 Hz/s` did not resolve the issue.
- HMI export history later showed additional REEL_UP_BELT changes, including acceleration up to `2400 Hz/s`.
- The B2 sensor bracket was found not to be square, corrected to a true 90-degree position, and sensor alignment was adjusted.
- Fault frequency reduced after bracket correction, but the fault persisted.

Current interpretation at the end of 2026-04-28:

- B12 had clean Modbus candidates but did not look like the only source.
- B1/B2 are likely represented in packed or encoded status words.
- The B1/B2 timing window near seal-bar-bottom became a stronger area of interest than further broad inverter tuning.
- The B2 bracket correction helped but did not fully solve the issue, suggesting either additional mechanical/electrical/timing contributors or controller interpretation of the sequence.

Reference files:

- `docs/handoff-2026-04-28.md`
- `docs/io-map-2026-04-28.md`
- `data/live_outputs/20260428/094009/`
- `data/videos/`
- `data/vnc_screenshots/`

### 2026-04-29 - Dashboard, HMI Export Parsing, Correlation, and Power-Cycle Test

Work completed:

- Fixed logger path handling and active-run routing.
- Added an `active_run.txt` pointer so scripts and WebUI use the intended run folder.
- Added single-instance logger handling to avoid multiple Modbus logger clients.
- Added a local WebUI/dashboard for field use at `http://127.0.0.1:8000`.
- Added WebUI fault markers so operator observations can be timestamped into the active run.
- Copied and parsed machine HMI exports:
  - `BP_ALVStoricAllarms.htm`
  - `BP_ALVStoricState.htm`
  - `BP_ALVStoricData.htm`
- Parsed:
  - `48,885` alarm/event records.
  - `36,228` machine state records.
  - `1,010` data/format change records.

HMI export findings:

- `PRODUCT FLOW END` appears to be expected low-product/waiting behavior and is not treated as the main root-cause target.
- `FILM FINISHED` is noisy context but not the primary diagnostic target.
- `BAR SAFETY` is the priority alarm.
- On 2026-04-29, BAR SAFETY events appeared repeatedly around:
  - `10:10`
  - `10:13`
  - `10:21`
  - `10:23`
  - `10:27-10:28`
  - `10:31`
  - `10:36`
  - `12:08`
- HMI state history around these timestamps repeatedly shows `SYSTEM RUNNING` transitioning into `SYSTEM IN STOP`.

BAR SAFETY to Modbus correlation:

- HMI BAR SAFETY ACTIVE events in export: `896`.
- Events inside the good Modbus run window: `11`.
- `11/11` had focused Modbus changes within +/-30 seconds.
- `11/11` had seal/B12 secondary movement within +/-30 seconds.
- `10/11` had B12 direct candidate movement within +/-30 seconds.
- `11/11` had B2 candidate movement within +/-30 seconds.
- The nearest focused Modbus change was often within roughly half a second of the HMI alarm timestamp.

Strongest current Modbus correlations:

- `10325`, `13539`: seal-bar or B12 secondary position.
- `10168`, `10182`: B1/B2 tied pair or B2 group.
- `13445`, `13505`: B12 direct candidates.

Modbus read failure and recovery:

- During afternoon testing, the logger could establish TCP connectivity to the machine but Modbus reads returned no values or were closed/reset.
- Duplicate logger processes were stopped and the dashboard was confirmed to read local files only.
- Direct laptop-to-machine connection was tested and showed the same read failure.
- The machine was power cycled.
- After power cycle, minimal Modbus reads succeeded again, including known registers such as `10050` and `10325`.
- A fresh healthy logger run started at `data/live_outputs/20260429/131837`.
- Full logging reported `ok_values=1300` per cycle.

Late 2026-04-29 product/fault observations:

- Operator reported three bad packs while run `20260429/131837` was actively logging.
- Marker `BAD_PACKS_3_REPORTED` was added at `2026-04-29T13:24:57.475-05:00`.
- The marker itself did not have a clean machine stop immediately beside it.
- Earlier in the same run, strong stop moments occurred at:
  - `13:21:50.880`, machine state `running -> stopped`.
  - `13:22:01.719`, machine state `running -> stopped`.
  - `13:22:10.409`, machine state `running -> stopped`.
- Those stop windows line up with B2 movement and seal/B12 secondary movement in the same 1-2 second neighborhood.
- `event_process_value` briefly decoded as `estop_or_safety_drop` at `13:21:56.308`.

Current interpretation at the end of 2026-04-29:

- The broad bad-pack marker at `13:24:57` may not represent the exact fault moment.
- The earlier `13:21:50`, `13:22:01`, and `13:22:10` windows look more like the BAR SAFETY / stop pattern.
- Those times should be compared to the next HMI alarm/state export to confirm exact alarm text.

Reference files:

- `docs/daily-log-2026-04-29.md`
- `docs/oem-machine-report-amendment-2026-04-29.md`
- `data/machine_exports/20260429_122132/summary.md`
- `data/machine_exports/20260429_122132/bar_safety_modbus_correlation.md`
- `data/live_outputs/20260429/131837/stop_sequence_132135_132220_summary.md`
- `data/live_outputs/20260429/131837/bad_packs_132457_summary.md`

## M715q / Edge Box Work

In parallel with the machine diagnostics, the Lenovo ThinkCentre M715q was prepared as the intended edge box for the project.

Completed:

- Documented BIOS baseline and boot posture.
- Built setup scripts for Ubuntu Server.
- Added M715q first-boot checks.
- Created the edge monitor web app under `edge_monitor/`.
- Verified the dashboard could run on the M715q in simulated mode.
- Started noVNC/websockify HMI viewer bridge.
- Confirmed the M715q dashboard was reachable at `http://192.168.8.197:8000` during the setup session.
- Shut the M715q down cleanly after capturing the runtime handoff.

Reference files:

- `docs/m715q-bios-baseline.md`
- `docs/ubuntu-server-first-boot.md`
- `docs/edge-monitor-app.md`
- `m715q_runtime_handoff_2026-04-29/`

## What Is Confirmed

- The machine can expose useful diagnostic data through Modbus TCP when reads are accepted.
- BAR SAFETY is repeatedly present in HMI alarm history.
- BAR SAFETY aligns with machine stop transitions in HMI state history.
- BAR SAFETY windows correlate strongly with B2, B12, and seal-bar secondary candidate Modbus values.
- B1/B2 are a tied pair, with B2 acting as the slave.
- B12 has clean Modbus candidates at `13445` and `13505`.
- Seal-bar/B12 secondary behavior has strong candidates at `10325` and `13539`.
- B2 bracket correction reduced fault frequency but did not resolve the problem.
- Inverter acceleration/deceleration tuning alone has not resolved the problem.
- B1/B2 sensors have been replaced, so the current investigation should include installation environment, wiring, heat, vibration, timing, and controller interpretation rather than assuming only failed sensor bodies.

## What Is Not Yet Confirmed

- A single dedicated Modbus bit for BAR SAFETY active.
- Exact controller logic that generates BAR SAFETY.
- Required timing/sequence among B1, B2, B12, seal-bar up/down, and safety inputs.
- Whether the remaining issue is primarily alignment, heat, wiring, electrical noise, timing, controller filtering, or a combination.
- Whether the `13:21:50`, `13:22:01`, and `13:22:10` stop windows from 2026-04-29 exactly match HMI BAR SAFETY without the next HMI export.
- Whether SSH or deeper system logs are OEM-supported and safe to access.

## OEM Support Requested

Targeted OEM support is requested in these areas:

1. BAR SAFETY logic definition:
   - Exact conditions that trigger BAR SAFETY.
   - Required sensor timing/sequence for B1, B2, B12, and seal-bar positions.
   - Whether BAR SAFETY has a dedicated internal variable, diagnostic page, or register.

2. Sensor validation:
   - Correct B1/B2/B12 alignment dimensions and tolerances.
   - Acceptable bracket angle and sensor-to-target distance.
   - Environmental guidance for SICK PN `1040752`, especially heat and vibration.

3. Electrical diagnostics:
   - Expected signal ranges at relevant inputs.
   - Filtering/debounce timing for the safety inputs.
   - Recommended test points for watching the safety chain during a fault.

4. Data access:
   - Official method to view raw I/O or diagnostic-level sensor states.
   - Whether SSH/log access is supported for diagnostics.
   - Any engineering tool or internal variable list for the BAR SAFETY chain.

5. Known issues:
   - Any documented bulletins or known failure modes for BAR SAFETY, B1/B2, B12, seal-bar safety, or this machine model.

## Immediate Next Steps

- Keep only one Modbus logger connected to the machine at a time.
- Use WebUI marker once per fault or bad pack when practical, instead of one marker after a cluster.
- After the next fault cluster, export HMI alarms/states and compare exact HMI alarm timestamps to Modbus windows.
- Physically observe B1/B2/B12 alignment and bracket movement during a running cycle, not only while stopped.
- Inspect B1/B2/B12 cables and connectors for heat damage, loose pins, intermittent strain, or motion during seal-bar movement.
- If faults appear after warmup, record sensor/bracket/cable temperatures at cold start and after faults.
- Do not bypass or defeat the safety chain during testing.

## Data Locations

- Daily log: `docs/daily-log-2026-04-29.md`
- OEM report amendment: `docs/oem-machine-report-amendment-2026-04-29.md`
- Machine export summary: `data/machine_exports/20260429_122132/summary.md`
- BAR SAFETY correlation: `data/machine_exports/20260429_122132/bar_safety_modbus_correlation.md`
- Latest healthy Modbus run: `data/live_outputs/20260429/131837/`
- Stop sequence review: `data/live_outputs/20260429/131837/stop_sequence_132135_132220_summary.md`
- Bad packs review: `data/live_outputs/20260429/131837/bad_packs_132457_summary.md`
- Known faults/fixes: `docs/known-faults-and-fixes.md`
- M715q handoff: `m715q_runtime_handoff_2026-04-29/`
