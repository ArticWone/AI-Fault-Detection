# OEM Machine Report Amendment - Work Performed Through 2026-04-29

This amendment expands the earlier OEM-facing report with the detailed work performed so far, including today's attempts, data captures, tooling changes, and current evidence.

## 1. Project Purpose

The project goal is to diagnose recurring SMI BP802ALV seal bar / BAR SAFETY / B1-B2-B12 related production faults using non-invasive machine observation:

- HMI alarm and state exports.
- Modbus TCP read-only logging.
- Operator timestamp markers.
- VNC/HMI screenshots where available.
- Controlled physical sensor tests.
- Focused correlation between machine faults and decoded register changes.

The logging system is diagnostic only. It does not command the machine, bypass safety, or write values to the controller.

## 2. Work Completed Before 2026-04-29

### 2.1 Workstation and Machine Connectivity

- Established direct Ethernet access to the machine.
- Confirmed machine services:
  - Modbus TCP on port 502.
  - VNC on port 5900.
  - SSH on port 22, visible but not used for diagnostics without OEM authorization.
- Set up Python environment and installed `pymodbus`.
- Built read-only Modbus logging tools:
  - Cold-start logger.
  - Broad live output logger.
  - Focused candidate sensor logger.
  - Operator marker script.
  - Decoder for turning register changes into readable state tables and timelines.

### 2.2 Initial Fault Logging

- Captured the first clean cold-start and live Modbus runs.
- Logged an observed production fault on 2026-04-27.
- Strong early fault-window candidate registers included:
  - `10190`
  - `10208`
  - `10209`
  - `10167`
  - `10168`
  - `10182`
  - `10217`
  - `10231`
- Register `10209` repeatedly flipped between `0` and `65535` before an observed fault.
- Registers `10190` and `10208` showed large changes near the fault window.

### 2.3 Physical Sensor / Control Mapping

Controlled tests were performed by tagging operator actions and comparing them against Modbus changes.

Current best mappings:

| Physical item | Best current Modbus candidate(s) | Evidence status |
| --- | --- | --- |
| Machine stopped/running state | `10059` | Strong |
| Running enable/value | `10189` | Strong |
| B1/B2 tied pair / B2 group | `10168`, `10182` | Strong paired-system candidate |
| B12 sensor | `13445`, `13505` | Strong |
| B12 / seal bar secondary position | `10325`, `13539` | Strong secondary candidate |
| Seal bar position down/up | `10325`, `13539`, secondary `13444`, `13504` | Strong |
| Top film-feed sensor | `10183` | Strong |
| E-stop / safety event process value | `10167` | Strong event candidate |
| B safety circuit electrical point | HMI DIO16 1 P13 / drawing E4.0.13 | Electrically confirmed; Modbus bit not isolated |

Important interpretation:

- B1 and B2 were clarified by the technician as a tied pair, with B2 acting as the slave.
- B2 should not be treated as an isolated standalone cause unless new evidence proves it.
- The recurring fault likely involves the B1/B2 timing window, seal-bar position, B12/safety chain state, or the way the controller interprets the combined sequence.

### 2.4 Mechanical / Tuning Attempts Before Today

- Film inverter acceleration and deceleration settings were tested.
- Lowering acceleration from `2000 Hz/s` to `1800 Hz/s` made failures worse.
- Raising acceleration to `2200 Hz/s` was reported as slightly better but not resolved.
- Deceleration tests at `900 Hz/s` and `1200 Hz/s` did not resolve the issue.
- Later HMI export history showed additional REEL_UP_BELT changes on 2026-04-28, including acceleration up to `2400 Hz/s`.
- B2 bracket was observed not to be a true 90 degrees and was corrected.
- Correcting bracket geometry reduced frequency but did not eliminate faults.
- B2 could not be bypassed by unplugging.

## 3. Work Attempted Today - 2026-04-29

### 3.1 Logger Path and Active Run Handling

The first work today was making the logger and marker workflow reliable on the current desktop project path.

Completed:

- Fixed Windows path handling where folder names with spaces broke the logger output directory.
- Updated the live logger to write an `active_run.txt` pointer.
- Updated marker scripts to write to the active run instead of guessing the newest folder.
- Updated startup tooling so helper scripts point to the current Desktop repo path.
- Added default behavior to stop previous logger instances before starting a new run.

Verification:

- Fresh live run folders were created under `data/live_outputs/20260429/`.
- Marker script successfully wrote to the intended active run.

### 3.2 Persistent Local Dashboard / WebUI

A lightweight local dashboard was added for live field use.

Completed:

- Added a Python standard-library HTTP dashboard at `http://127.0.0.1:8000`.
- Added tabs:
  - Restored Log.
  - HMI Picture.
  - Live Log.
  - Live Changes.
- Added API endpoints for:
  - Persistent state.
  - Current run state.
  - Latest HMI snapshot.
  - WebUI fault markers.
- Dashboard restores the last informative run instead of only showing the newest active run.

Verification:

- Dashboard compiled and returned HTTP 200.
- API endpoints returned current run metadata.
- WebUI marker endpoint successfully wrote operator markers.

### 3.3 Machine HMI Export Copied and Parsed

Machine history exports were copied from the machine drive and parsed.

Source files:

- `BP_ALVStoricAllarms.htm`
- `BP_ALVStoricState.htm`
- `BP_ALVStoricData.htm`

Parsed results:

- 48,885 alarm/event records.
- 36,228 machine state records.
- 1,010 data/format change records.

Important findings:

- `PRODUCT FLOW END` appears to be expected low-product/waiting behavior and should not be the main root-cause target.
- `FILM FINISHED` is noisy context but not the main current diagnostic target.
- `BAR SAFETY` is the priority alarm.
- On 2026-04-29, BAR SAFETY repeatedly appeared around:
  - `10:10:03`
  - `10:13:17`
  - `10:13:22`
  - `10:21:06`
  - `10:23:27`
  - `10:27:38`
  - `10:28:00`
  - `10:31:03`
  - `10:36:09`
  - `10:36:18`
  - `10:36:29`
  - `12:08:07`
  - `12:08:16`
  - `12:08:26`
- State history around these events repeatedly shows the machine moving from SYSTEM RUNNING into SYSTEM IN STOP.

### 3.4 BAR SAFETY to Modbus Correlation

The HMI BAR SAFETY active timestamps were compared to a good Modbus run from the morning.

Result:

- HMI BAR SAFETY ACTIVE events in export: 896.
- Events inside the good Modbus run window: 11.
- All 11 had focused Modbus changes within +/-30 seconds.
- All 11 had seal/B12 secondary movement within +/-30 seconds.
- 10 of 11 had B12 direct candidate movement within +/-30 seconds.
- All 11 had B2 candidate movement within +/-30 seconds.
- The nearest focused Modbus change was often within roughly half a second of the HMI alarm timestamp.

Current interpretation:

- The HMI alarm and HMI state clocks are internally consistent.
- Modbus changes correlate strongly with the B2 / B12 / seal-bar secondary chain around BAR SAFETY events.
- We still have not isolated a single clean Modbus bit that equals "BAR SAFETY active."
- The strongest current Modbus correlation is the seal/B12 secondary pair at `10325` and `13539`, especially transitions involving the decoded `seal_bar_up_or_B12_tripped_secondary` state.

### 3.5 B1/B2 Sensor Replacement Context

Today it was recorded that B1/B2 sensors were replaced.

Sensor part information:

- B1/B2 use SICK sensor PN `1040752`.

Current interpretation:

- Since B1/B2 sensor bodies have been replaced, the sensor body itself is not the first suspect unless new evidence points back to it.
- The open concern is still the installed environment:
  - Alignment.
  - Bracket movement or flex.
  - Heat exposure.
  - Connector or cable strain.
  - Input timing at the safety/PLC side.
- OEM position reported by the user: placement is acceptable and sensors should tolerate the location.
- In-house concern remains that heat at the mounting area may contribute to failures or unstable behavior.

### 3.6 Modbus Read Failure Investigation

During the afternoon, the logger began connecting at TCP level but receiving no valid Modbus values. The machine closed or reset reads.

Attempted:

- Restarted logger runs.
- Tested exact known-good registers from earlier runs.
- Confirmed TCP connectivity to `192.168.0.1:502`.
- Stopped duplicate logger processes.
- Added a single-instance lock so only one live Modbus logger can run at a time.
- Confirmed the dashboard reads local files only and does not connect to the machine.
- Tested direct laptop-to-machine connection, removing the switch and diagnostic node from the path.

Findings:

- TCP connection succeeded but Modbus reads returned no values.
- The issue persisted even on direct laptop connection.
- The machine does not expect or require the diagnostic node; the node/logger is an added diagnostic tool.
- Current evidence points to a machine endpoint/session/read-state issue rather than a required diagnostic-node IP address.

### 3.7 Machine Power Cycle and Restored Modbus Logging

The machine was power cycled.

After power cycle:

- Minimal reads succeeded again.
- Known registers such as `10050` and `10325` returned values.
- A fresh run started at `data/live_outputs/20260429/131837`.
- Full logger became healthy with `ok_values=1300` per cycle.
- `changes.csv` began receiving live changes.
- WebUI fault marker path successfully wrote to the fresh active run.

Interpretation:

- Power cycling restored the machine's ability to answer Modbus reads.
- This supports the idea that the earlier failure was an endpoint/session/read-state problem, not a basic cable/IP problem.

### 3.8 Three Bad Packs During Healthy Logging

During healthy logging, the operator reported three more bad packs.

Marker:

- `2026-04-29T13:24:57.475-05:00`, `BAD_PACKS_3_REPORTED`.

Findings:

- Logger remained healthy with `ok_values=1300`.
- In the 90 seconds before the marker, there was heavy B2/seal-bar/B12-related movement, but no machine-state stop immediately beside the report marker.
- Earlier in the same run, the strongest stop moments were:
  - `13:21:50.880`, machine state `running -> stopped`.
  - `13:22:01.719`, machine state `running -> stopped`.
  - `13:22:10.409`, machine state `running -> stopped`.
- Each of those stop moments lined up with B2 movement and seal/B12 secondary movement in the same 1-2 second neighborhood.
- `event_process_value` briefly decoded as `estop_or_safety_drop` at `13:21:56.308`.

Current interpretation:

- The broad bad-pack marker at `13:24:57` does not look like a clean BAR SAFETY stop right at the marker time.
- The earlier `13:21:50`, `13:22:01`, and `13:22:10` windows look much closer to the BAR SAFETY / stop pattern.
- These times should be compared against a fresh HMI export after the run to confirm exact alarm text.

## 4. Current Working Theory

The most likely fault area remains the B1/B2/B12/seal-bar safety sequence rather than a simple single failed sensor.

The evidence points toward:

- Brief safety-chain drop or timing mismatch during seal-bar / B2 / B12 movement.
- B1/B2 paired sensor timing or alignment issue.
- B12 / seal-bar secondary state interacting with the safety logic.
- Possible heat, vibration, bracket movement, or cable/connector instability near the B1/B2/B12 mounting area.
- Controller interpretation of the sensor sequence, especially when product/film position is marginal.

The issue does not appear solved by inverter acceleration/deceleration changes alone.

## 5. What Is Confirmed vs Not Confirmed

Confirmed:

- BAR SAFETY is repeatedly present in the HMI alarm export.
- BAR SAFETY events correspond with SYSTEM IN STOP transitions in the HMI state export.
- Modbus candidate changes around BAR SAFETY strongly involve B2, B12, and seal-bar secondary values.
- B1/B2 are tied, and B2 is the slave.
- B12 has clean Modbus candidates at `13445` and `13505`.
- Seal-bar/B12 secondary values have strong candidates at `10325` and `13539`.
- A direct Modbus read path can work after machine power cycle.
- Duplicate diagnostic loggers should be avoided.

Not yet confirmed:

- A single dedicated Modbus bit for BAR SAFETY active.
- Whether the fault is caused by sensor alignment, heat, wiring, timing, controller safety logic, or a combination.
- Whether the 13:21 stop windows from today exactly match HMI BAR SAFETY until the next HMI export is reviewed.
- Whether SSH or deeper system logs are OEM-supported and safe to access.

## 6. Recommended OEM Support Requests

Please ask OEM to help with:

1. BAR SAFETY logic definition:
   - Exact controller conditions that generate BAR SAFETY.
   - Required sequence/timing among B1, B2, B12, seal-bar up/down, and safety inputs.
   - Whether BAR SAFETY has a dedicated internal variable or diagnostic page.

2. Sensor tolerance and installation:
   - Correct B1/B2/B12 alignment dimensions.
   - Acceptable bracket angle and sensor-to-target distance.
   - Heat tolerance and recommended shielding or cable routing for SICK PN `1040752`.
   - Whether the B1/B2 area is known to suffer heat-related sensor or connector issues.

3. Electrical diagnostics:
   - Expected voltage levels at the relevant safety/PLC inputs.
   - Filtering/debounce timing for the B1/B2/B12/safety chain.
   - Recommended test points for watching the safety input during a fault.

4. Data access:
   - Official method for reading raw I/O or diagnostic bits.
   - Whether SSH access is supported for logs only, and what credentials/procedure are approved.
   - Register map or engineering page for BAR SAFETY and related sensor states.

5. Known issues:
   - Any firmware, parameter, sensor mounting, or wiring bulletins related to BAR SAFETY, B1/B2, B12, or seal-bar safety faults on this machine model.

## 7. Recommended Next Diagnostic Steps

- Keep only one Modbus logger connected at a time.
- Use the WebUI fault button once per bad pack or fault event, if practical, instead of one marker after a cluster.
- After each fault cluster, export HMI alarms/states again and compare exact HMI alarm times to Modbus windows.
- During a running cycle, physically watch B1/B2/B12 alignment and bracket movement, not only static alignment while stopped.
- Check cables/connectors for heat damage, loose pins, strain, or motion during seal-bar movement.
- If the problem appears after warmup, record sensor, bracket, and cable temperatures at cold start and after faults.
- Do not bypass or defeat the safety chain during testing.

## 8. Current Status at Close of 2026-04-29 Work

- Project services/loggers were stopped at close of work.
- The latest healthy logging run was `data/live_outputs/20260429/131837`.
- The best current evidence is in:
  - `docs/daily-log-2026-04-29.md`
  - `data/machine_exports/20260429_122132/summary.md`
  - `data/machine_exports/20260429_122132/bar_safety_modbus_correlation.md`
  - `data/live_outputs/20260429/131837/stop_sequence_132135_132220_summary.md`
  - `data/live_outputs/20260429/131837/bad_packs_132457_summary.md`
- The investigation is narrowed to the BAR SAFETY / B1-B2 / B12 / seal-bar safety chain, with the strongest live Modbus correlation currently around `10325`, `13539`, `10168`, `10182`, `13445`, and `13505`.
