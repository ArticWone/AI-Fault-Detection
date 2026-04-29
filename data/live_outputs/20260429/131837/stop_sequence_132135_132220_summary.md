# Stop Sequence Review - 13:21:35 to 13:22:20

Run: `data/live_outputs/20260429/131837`

## Result

- The later `BAD_PACKS_3_REPORTED` marker at `13:24:57` did not have a stop right beside it.
- The earlier `13:21:35-13:22:20` window did contain several real stop/running transitions.
- The three strongest stop moments were `13:21:50.880`, `13:22:01.719`, and `13:22:10.409`.
- Each stop moment lines up with B2 movement and seal/B12 secondary movement in the same 1-2 second neighborhood.
- `event_process_value` briefly decoded as `estop_or_safety_drop` at `13:21:56.308`, shortly after the first stop/restart sequence.

## Machine State Changes

- `2026-04-29T13:21:42.234` `observed:5` -> `gates_closed_hold_down` raw `5` -> `13`
- `2026-04-29T13:21:45.482` `gates_closed_hold_down` -> `running` raw `13` -> `3`
- `2026-04-29T13:21:50.880` `running` -> `stopped` raw `3` -> `11`
- `2026-04-29T13:21:55.229` `stopped` -> `running` raw `11` -> `3`
- `2026-04-29T13:22:01.719` `running` -> `stopped` raw `3` -> `11`
- `2026-04-29T13:22:02.800` `stopped` -> `running` raw `11` -> `3`
- `2026-04-29T13:22:10.409` `running` -> `stopped` raw `3` -> `11`

## Stop Neighborhoods

### Around 2026-04-29T13:21:50.880
- `2026-04-29T13:21:48.724` `b2_bottle_down_group_b`: `observed:321` -> `observed:318` raw `321` -> `318`
- `2026-04-29T13:21:48.724` `event_process_value`: `process:1290` -> `process:1296` raw `1290` -> `1296`
- `2026-04-29T13:21:48.724` `state_code_primary`: `observed:24` -> `running_code` raw `24` -> `32`
- `2026-04-29T13:21:48.724` `seal_bar_position_b`: `observed:23842` -> `B12_clear_secondary` raw `23842` -> `23881`
- `2026-04-29T13:21:49.806` `b2_sensor_group_a`: `observed:318` -> `observed:324` raw `318` -> `324`
- `2026-04-29T13:21:49.806` `b2_bottle_down_group_b`: `observed:318` -> `observed:323` raw `318` -> `323`
- `2026-04-29T13:21:49.806` `event_process_value`: `process:1296` -> `process:1293` raw `1296` -> `1293`
- `2026-04-29T13:21:49.806` `state_code_primary`: `running_code` -> `observed:34` raw `32` -> `34`
- `2026-04-29T13:21:50.880` `machine_state`: `running` -> `stopped` raw `3` -> `11`
- `2026-04-29T13:21:50.880` `running_enable`: `running` -> `observed:776` raw `1000` -> `776`
- `2026-04-29T13:21:50.880` `b2_sensor_group_a`: `observed:324` -> `B2_released` raw `324` -> `326`
- `2026-04-29T13:21:50.880` `b2_bottle_down_group_b`: `observed:323` -> `observed:324` raw `323` -> `324`
- `2026-04-29T13:21:50.880` `event_process_value`: `process:1293` -> `process:1126` raw `1293` -> `1126`
- `2026-04-29T13:21:50.880` `state_code_primary`: `observed:34` -> `observed:20` raw `34` -> `20`
- `2026-04-29T13:21:51.963` `running_enable`: `observed:776` -> `not_running` raw `776` -> `0`
- `2026-04-29T13:21:51.963` `b2_bottle_down_group_b`: `observed:324` -> `observed:326` raw `324` -> `326`
- `2026-04-29T13:21:51.963` `event_process_value`: `process:1126` -> `process:1375` raw `1126` -> `1375`
- `2026-04-29T13:21:51.963` `state_code_primary`: `observed:20` -> `observed:3` raw `20` -> `3`
- `2026-04-29T13:21:51.963` `seal_bar_position_a`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:21:51.963` `seal_bar_position_b`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:21:53.049` `b2_sensor_group_a`: `B2_released` -> `observed_high` raw `326` -> `328`
- `2026-04-29T13:21:53.049` `b2_bottle_down_group_b`: `observed:326` -> `observed:329` raw `326` -> `329`
- `2026-04-29T13:21:53.049` `event_process_value`: `process:1375` -> `process:1378` raw `1375` -> `1378`
- `2026-04-29T13:21:53.049` `state_code_primary`: `observed:3` -> `observed:6` raw `3` -> `6`

### Around 2026-04-29T13:22:01.719
- `2026-04-29T13:21:59.555` `b2_sensor_group_a`: `observed:323` -> `observed:322` raw `323` -> `322`
- `2026-04-29T13:21:59.555` `b2_bottle_down_group_b`: `observed:322` -> `observed:321` raw `322` -> `321`
- `2026-04-29T13:21:59.555` `event_process_value`: `process:1297` -> `process:1294` raw `1297` -> `1294`
- `2026-04-29T13:21:59.555` `state_code_primary`: `observed:36` -> `observed:34` raw `36` -> `34`
- `2026-04-29T13:21:59.555` `seal_bar_position_secondary_a`: `seal_bar_down` -> `observed:163` raw `164` -> `163`
- `2026-04-29T13:21:59.555` `seal_bar_position_secondary_b`: `seal_bar_down` -> `observed:163` raw `164` -> `163`
- `2026-04-29T13:22:00.633` `event_process_value`: `process:1294` -> `process:1129` raw `1294` -> `1129`
- `2026-04-29T13:22:00.633` `state_code_primary`: `observed:34` -> `observed:24` raw `34` -> `24`
- `2026-04-29T13:22:01.719` `machine_state`: `running` -> `stopped` raw `3` -> `11`
- `2026-04-29T13:22:01.719` `running_enable`: `running` -> `not_running` raw `1000` -> `0`
- `2026-04-29T13:22:01.719` `b2_sensor_group_a`: `observed:322` -> `observed:318` raw `322` -> `318`
- `2026-04-29T13:22:01.719` `b2_bottle_down_group_b`: `observed:321` -> `observed:319` raw `321` -> `319`
- `2026-04-29T13:22:01.719` `event_process_value`: `process:1129` -> `process:1374` raw `1129` -> `1374`
- `2026-04-29T13:22:01.719` `state_code_primary`: `observed:24` -> `observed:17` raw `24` -> `17`
- `2026-04-29T13:22:01.719` `seal_bar_position_a`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:22:01.719` `seal_bar_position_b`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:22:02.800` `machine_state`: `stopped` -> `running` raw `11` -> `3`
- `2026-04-29T13:22:02.800` `b2_sensor_group_a`: `observed:318` -> `observed:321` raw `318` -> `321`
- `2026-04-29T13:22:02.800` `b2_bottle_down_group_b`: `observed:319` -> `observed:322` raw `319` -> `322`
- `2026-04-29T13:22:02.800` `event_process_value`: `process:1374` -> `process:1366` raw `1374` -> `1366`
- `2026-04-29T13:22:02.800` `state_code_primary`: `observed:17` -> `observed:12` raw `17` -> `12`
- `2026-04-29T13:22:02.800` `seal_bar_position_a`: `seal_bar_up_or_B12_tripped_secondary` -> `B12_clear_secondary` raw `23920` -> `23881`
- `2026-04-29T13:22:02.800` `seal_bar_position_b`: `seal_bar_up_or_B12_tripped_secondary` -> `B12_clear_secondary` raw `23920` -> `23881`
- `2026-04-29T13:22:03.895` `b2_sensor_group_a`: `observed:321` -> `observed:320` raw `321` -> `320`
- `2026-04-29T13:22:03.895` `b2_bottle_down_group_b`: `observed:322` -> `observed:320` raw `322` -> `320`
- `2026-04-29T13:22:03.895` `event_process_value`: `process:1366` -> `process:20` raw `1366` -> `20`
- `2026-04-29T13:22:03.895` `state_code_primary`: `observed:12` -> `observed:22` raw `12` -> `22`

### Around 2026-04-29T13:22:10.409
- `2026-04-29T13:22:08.217` `event_process_value`: `process:1283` -> `process:1417` raw `1283` -> `1417`
- `2026-04-29T13:22:09.318` `b2_sensor_group_a`: `observed:316` -> `observed:318` raw `316` -> `318`
- `2026-04-29T13:22:09.318` `b2_bottle_down_group_b`: `observed:316` -> `observed:317` raw `316` -> `317`
- `2026-04-29T13:22:09.318` `event_process_value`: `process:1417` -> `process:1127` raw `1417` -> `1127`
- `2026-04-29T13:22:09.318` `state_code_primary`: `observed:21` -> `observed:23` raw `21` -> `23`
- `2026-04-29T13:22:10.409` `machine_state`: `running` -> `stopped` raw `3` -> `11`
- `2026-04-29T13:22:10.409` `b2_sensor_group_a`: `observed:318` -> `observed:324` raw `318` -> `324`
- `2026-04-29T13:22:10.409` `b2_bottle_down_group_b`: `observed:317` -> `observed:323` raw `317` -> `323`
- `2026-04-29T13:22:10.409` `event_process_value`: `process:1127` -> `process:1491` raw `1127` -> `1491`
- `2026-04-29T13:22:10.409` `state_code_primary`: `observed:23` -> `observed:12` raw `23` -> `12`
- `2026-04-29T13:22:10.409` `seal_bar_position_a`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:22:10.409` `seal_bar_position_b`: `B12_clear_secondary` -> `seal_bar_up_or_B12_tripped_secondary` raw `23881` -> `23920`
- `2026-04-29T13:22:11.495` `b2_sensor_group_a`: `observed:324` -> `observed:316` raw `324` -> `316`
- `2026-04-29T13:22:11.495` `b2_bottle_down_group_b`: `observed:323` -> `observed:316` raw `323` -> `316`
- `2026-04-29T13:22:11.495` `event_process_value`: `process:1491` -> `process:1385` raw `1491` -> `1385`
- `2026-04-29T13:22:11.495` `state_code_primary`: `observed:12` -> `observed:6` raw `12` -> `6`
- `2026-04-29T13:22:12.589` `b2_bottle_down_group_b`: `observed:316` -> `observed:315` raw `316` -> `315`
- `2026-04-29T13:22:12.589` `event_process_value`: `process:1385` -> `process:1381` raw `1385` -> `1381`
- `2026-04-29T13:22:12.589` `state_code_primary`: `observed:6` -> `observed:7` raw `6` -> `7`
- `2026-04-29T13:22:12.589` `seal_bar_position_a`: `seal_bar_up_or_B12_tripped_secondary` -> `seal_bar_down` raw `23920` -> `23959`
- `2026-04-29T13:22:12.589` `seal_bar_position_b`: `seal_bar_up_or_B12_tripped_secondary` -> `seal_bar_down` raw `23920` -> `23959`

## Interpretation

- This window looks much closer to the earlier BAR SAFETY correlation pattern than the later broad bad-pack report marker.
- It still does not identify a single proven HMI alarm bit, but it points back to the B2/seal-bar/B12 chain at the exact stop moments.
- If these stop moments line up with the three bad packs physically observed, this is the window to compare against the HMI alarm export after the run.
