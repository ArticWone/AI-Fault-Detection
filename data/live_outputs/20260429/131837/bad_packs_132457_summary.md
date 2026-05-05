# Bad Packs Report - 13:24:57

Active run: `data/live_outputs/20260429/131837`

Marker:
- `2026-04-29T13:24:57.475-05:00 BAD_PACKS_3_REPORTED`

Logger status:
- Healthy after power cycle; run log continued at `ok_values=1300` per cycle.
- Marker was added after the operator report, so the exact bad-pack timestamps are approximate unless separate button presses are made per pack.

## Window last_4_min_to_20_sec_after
- Range: `2026-04-29T13:20:57.475000` to `2026-04-29T13:25:17.475000`
- Focused changes: 853
- b12_sensor_a: 13
- b12_sensor_b: 13
- b2_bottle_down_group_b: 109
- b2_sensor_group_a: 131
- event_process_value: 226
- machine_state: 7
- running_enable: 9
- seal_bar_position_a: 86
- seal_bar_position_b: 88
- seal_bar_position_secondary_a: 10
- seal_bar_position_secondary_b: 10
- state_code_primary: 151

Machine-state changes:
- `2026-04-29T13:21:42.234` observed:5 -> gates_closed_hold_down (5 -> 13)
- `2026-04-29T13:21:45.482` gates_closed_hold_down -> running (13 -> 3)
- `2026-04-29T13:21:50.880` running -> stopped (3 -> 11)
- `2026-04-29T13:21:55.229` stopped -> running (11 -> 3)
- `2026-04-29T13:22:01.719` running -> stopped (3 -> 11)
- `2026-04-29T13:22:02.800` stopped -> running (11 -> 3)
- `2026-04-29T13:22:10.409` running -> stopped (3 -> 11)
Running-enable changes:
- `2026-04-29T13:21:42.234` running -> not_running (1000 -> 0)
- `2026-04-29T13:21:47.639` not_running -> running (0 -> 1000)
- `2026-04-29T13:21:50.880` running -> observed:776 (1000 -> 776)
- `2026-04-29T13:21:51.963` observed:776 -> not_running (776 -> 0)
- `2026-04-29T13:21:57.394` not_running -> observed:960 (0 -> 960)
- `2026-04-29T13:21:58.473` observed:960 -> running (960 -> 1000)
- `2026-04-29T13:22:01.719` running -> not_running (1000 -> 0)
- `2026-04-29T13:22:06.064` not_running -> running (0 -> 1000)
- `2026-04-29T13:22:15.851` running -> not_running (1000 -> 0)

## Window last_90_sec_to_20_sec_after
- Range: `2026-04-29T13:23:27.475000` to `2026-04-29T13:25:17.475000`
- Focused changes: 357
- b12_sensor_a: 6
- b12_sensor_b: 6
- b2_bottle_down_group_b: 47
- b2_sensor_group_a: 54
- event_process_value: 94
- seal_bar_position_a: 43
- seal_bar_position_b: 43
- seal_bar_position_secondary_a: 4
- seal_bar_position_secondary_b: 4
- state_code_primary: 56

Machine-state changes: none in this window.
Running-enable changes: none in this window.

## Interpretation

- This bad-pack report is not the same as a clean BAR SAFETY stop in the log. There was heavy B2/seal-bar/B12-related movement, but no machine-state stop right at the report marker.
- There were stop/running transitions earlier in the run around `13:21:50`, `13:22:01`, and `13:22:10`; those may be separate operator/machine events unless they line up with the actual bad-pack moments.
- For the next bad packs, press the WebUI fault button once per bad pack if possible. That will let us isolate a +/-10 second window around each pack instead of treating the whole several-minute stretch as one event.
