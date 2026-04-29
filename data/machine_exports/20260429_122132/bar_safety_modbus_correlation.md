# BAR SAFETY vs Modbus Correlation

Source files:
- HMI alarms: `c:/Users/Jared/Desktop/WORK/SMI AI Thing/AI-Fault-Detection-push-20260428/data/machine_exports/20260429_122132/alarms.csv`
- Modbus decoded changes: `c:/Users/Jared/Desktop/WORK/SMI AI Thing/AI-Fault-Detection-push-20260428/data/live_outputs/20260429/092625/decoded_changes.csv`

Method: each HMI `BAR SAFETY` ACTIVE event was compared to decoded Modbus signal changes within +/-30 seconds, with a closest-change delta retained for clock/polling sanity checks.

## Result

- HMI `BAR SAFETY` ACTIVE events in export: 896
- Events inside the good Modbus run window: 11
- Events outside the Modbus run window: 885
- Any focused Modbus change within +/-30s: 11/11
- Seal/B12 secondary change within +/-30s: 11/11
- B12 direct candidate change within +/-30s: 10/11
- B2 candidate change within +/-30s: 11/11
- Machine-state stopped change within +/-30s: 1/11

Interpretation: the HMI alarm log and state log match exactly for `BAR SAFETY`/`SYSTEM IN STOP`, so the HMI clock is internally consistent. The Modbus timeline does show correlating movement on the seal-bar/B12/B2 candidate registers around many BAR SAFETY events, but not a clean one-register, same-second alarm bit yet. The best Modbus correlation currently appears to be the seal/B12 secondary pair `seal_bar_position_a`/`seal_bar_position_b` at addresses 10325 and 13539, especially transitions involving `seal_bar_up_or_B12_tripped_secondary`.

This means Modbus can likely help correlate the physical bar/B12 chain to the HMI error, but we should treat these as candidate process/safety signals until we catch a fresh fault with the logger and fault marker working.

## Current-Morning BAR SAFETY Events

These are the 2026-04-29 events that were inside the good Modbus run:

| HMI BAR SAFETY active | Nearest focused Modbus change | B2 | B12 direct | Seal/B12 secondary | Machine stopped |
| --- | ---: | --- | --- | --- | --- |
| 10:10:03 | -0.482s | yes | yes | yes | no |
| 10:13:17 | -0.196s | yes | yes | yes | no |
| 10:13:22 | +0.199s | yes | yes | yes | no |
| 10:21:06 | +0.411s | yes | yes | yes | no |
| 10:23:27 | -0.258s | yes | yes | yes | no |
| 10:27:38 | +0.345s | yes | no | yes | no |
| 10:28:00 | -0.048s | yes | yes | yes | no |
| 10:31:03 | -0.513s | yes | yes | yes | yes |
| 10:36:09 | +0.097s | yes | yes | yes | no |
| 10:36:18 | -0.274s | yes | yes | yes | no |
| 10:36:29 | -0.501s | yes | yes | yes | no |

The 12:08 BAR SAFETY events were outside the good Modbus run window, so they cannot be confirmed from that run.

## Examples

- `2026-04-29T10:10:03`: nearest focused Modbus change -0.482s; B2=yes, B12=yes, seal/B12 secondary=yes.
  - -0.5s B2/Bottle-down B: observed:318 -> observed:317
  - -0.5s State code primary: bottle_down_tripped_code -> observed:31
  - +0.6s B2/Bottle-down B: observed:317 -> observed:316
  - +0.6s B2 A: observed:318 -> observed:317
- `2026-04-29T10:13:17`: nearest focused Modbus change -0.196s; B2=yes, B12=yes, seal/B12 secondary=yes.
  - -0.2s B2/Bottle-down B: observed:320 -> observed:326
  - -0.2s B2 A: observed:320 -> B2_held
  - -0.2s State code primary: observed:28 -> bottle_down_clear_code
  - -1.3s B2/Bottle-down B: observed:325 -> observed:320
- `2026-04-29T10:13:22`: nearest focused Modbus change +0.199s; B2=yes, B12=yes, seal/B12 secondary=yes.
  - +0.2s B2/Bottle-down B: observed:325 -> observed:326
  - +0.2s B2 A: B2_released -> B2_held
  - +0.2s Seal secondary A: seal_bar_down -> observed:165
  - +0.2s Seal secondary B: seal_bar_down -> observed:165
- `2026-04-29T10:21:06`: nearest focused Modbus change +0.411s; B2=yes, B12=yes, seal/B12 secondary=yes.
  - +0.4s B2/Bottle-down B: observed:315 -> observed:319
  - +0.4s B2 A: observed:316 -> observed:319
  - +0.4s Running enable: observed:96 -> not_running
  - +0.4s Seal/B12 secondary A: seal_bar_up_or_B12_tripped_secondary -> seal_bar_down
- `2026-04-29T10:23:27`: nearest focused Modbus change -0.258s; B2=yes, B12=yes, seal/B12 secondary=yes.
  - -0.3s B2/Bottle-down B: observed:316 -> observed:317
  - -0.3s B2 A: observed:317 -> observed:321
  - -0.3s State code primary: observed:27 -> observed:31
  - +0.8s B2 A: observed:321 -> observed:318
- `2026-04-29T10:27:38`: nearest focused Modbus change +0.345s; B2=yes, B12=no, seal/B12 secondary=yes.
  - +0.3s B2 A: B2_released -> observed:325
  - +0.3s State code primary: observed:33 -> observed:28
  - -0.7s B2/Bottle-down B: observed:317 -> observed:324
  - -0.7s B2 A: observed:317 -> B2_released

Full table: `c:/Users/Jared/Desktop/WORK/SMI AI Thing/AI-Fault-Detection-push-20260428/data/machine_exports/20260429_122132/bar_safety_modbus_correlation.csv`
