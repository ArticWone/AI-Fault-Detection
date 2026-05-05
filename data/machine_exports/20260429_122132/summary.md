# Machine Export Summary - 2026-04-29 12:21

Source files copied from `D:\` into this folder.

## Parsed Counts
- Alarms/events: 48885
- Machine states: 36228
- Data/format changes: 1010

## Most Recent Alarms
- 2026-04-29T12:14:04 RESOLVED E_ID 7 FILM FINISHED
- 2026-04-29T12:08:38 ACTIVE E_ID 7 FILM FINISHED
- 2026-04-29T12:08:30 RESOLVED E_ID 14 BAR SAFETY
- 2026-04-29T12:08:26 ACTIVE E_ID 14 BAR SAFETY
- 2026-04-29T12:08:19 RESOLVED E_ID 14 BAR SAFETY
- 2026-04-29T12:08:16 ACTIVE E_ID 14 BAR SAFETY
- 2026-04-29T12:08:09 RESOLVED E_ID 14 BAR SAFETY
- 2026-04-29T12:08:07 ACTIVE E_ID 14 BAR SAFETY
- 2026-04-29T12:06:34 RESOLVED E_ID 21 PRODUCT FLOW END
- 2026-04-29T12:01:34 ACTIVE E_ID 21 PRODUCT FLOW END
- 2026-04-29T11:44:00 RESOLVED E_ID 7 FILM FINISHED
- 2026-04-29T10:36:38 ACTIVE E_ID 7 FILM FINISHED
- 2026-04-29T10:36:30 RESOLVED E_ID 14 BAR SAFETY
- 2026-04-29T10:36:29 ACTIVE E_ID 14 BAR SAFETY
- 2026-04-29T10:36:21 RESOLVED E_ID 14 BAR SAFETY

## Active Alarm Frequency
- 11456x E_ID 56 Product Lack
- 7949x E_ID 21 PRODUCT FLOW END
- 1657x E_ID 32 PRESS POWER
- 920x E_ID 2 EMERGENCY DOOR OPEN 1
- 896x E_ID 14 BAR SAFETY
- 446x E_ID 7 FILM FINISHED
- 325x E_ID 25 B12 OBSTRUCTION
- 205x E_ID 40 NO PRESSURE
- 156x E_ID 43 INVERTER ERROR [ ]
- 152x E_ID 3 EMERGENCY DOOR OPEN 2
- 98x E_ID 9 UNWINDER PROBLEM 1
- 65x E_ID 33 EMERGENCY

## Most Recent Machine States
- 2026-04-29T12:15:08 ID 11 SYSTEM RUNNING
- 2026-04-29T12:08:55 ID 9 SYSTEM IN STOP
- 2026-04-29T12:08:38 ID 8 STOPPING SYSTEM
- 2026-04-29T12:08:31 ID 11 SYSTEM RUNNING
- 2026-04-29T12:08:26 ID 9 SYSTEM IN STOP
- 2026-04-29T12:08:20 ID 11 SYSTEM RUNNING
- 2026-04-29T12:08:16 ID 9 SYSTEM IN STOP
- 2026-04-29T12:08:10 ID 11 SYSTEM RUNNING
- 2026-04-29T12:08:07 ID 9 SYSTEM IN STOP
- 2026-04-29T12:06:35 ID 11 SYSTEM RUNNING
- 2026-04-29T12:01:34 ID 16 SYSTEM IN PAUSE
- 2026-04-29T12:01:34 ID 8 STOPPING SYSTEM
- 2026-04-29T11:44:10 ID 11 SYSTEM RUNNING
- 2026-04-29T10:36:51 ID 9 SYSTEM IN STOP
- 2026-04-29T10:36:38 ID 8 STOPPING SYSTEM

## Most Recent Data Changes
- 2026-04-28T13:59:11 D_CHANGE REEL_UP_BELT ID_D 23287 Acceleration Ramp [Hz/s] from 2200 to 2400
- 2026-04-28T13:29:29 D_CHANGE REEL_UP_BELT ID_D 23287 Acceleration Ramp [Hz/s] from 2000 to 2200
- 2026-04-28T13:29:25 D_CHANGE REEL_UP_BELT ID_D 23302 Deceleration Ramp [Hz/s] from 1200 to 1000
- 2026-04-28T13:29:15 D_CHANGE REEL_UP_BELT ID_D 23002 Inverter Frequency Increase [Hz/ms] from 10.0 to 20.0
- 2026-04-28T13:10:34 D_CHANGE REEL_UP_BELT ID_D 23002 Inverter Frequency Increase [Hz/ms] from 20.0 to 10.0
- 2026-04-28T13:00:39 D_CHANGE REEL_UP_BELT ID_D 23302 Deceleration Ramp [Hz/s] from 1000 to 1200
- 2026-04-28T12:21:51 D_CHANGE REEL_UP_BELT ID_D 23302 Deceleration Ramp [Hz/s] from 900 to 1000
- 2026-04-28T12:21:46 D_CHANGE REEL_UP_BELT ID_D 23287 Acceleration Ramp [Hz/s] from 2200 to 2000
- 2026-04-28T12:17:19 D_CHANGE REEL_UP_BELT ID_D 23287 Acceleration Ramp [Hz/s] from 1800 to 2200
- 2026-04-28T12:03:34 D_CHANGE REEL_UP_BELT ID_D 23287 Acceleration Ramp [Hz/s] from 2000 to 1800
- 2026-04-28T11:28:54 D_CHANGE REEL_UP_BELT ID_D 23302 Deceleration Ramp [Hz/s] from 1000 to 900
- 2026-04-23T09:46:08 D_CHANGE M10 6X4Nested20oz ID_D 13614 Oven Belt - Loading Position Correction [mm] from 30 to 10
- 2026-04-23T09:45:12 F_CHANGE From: M06 To: M10 ID_D 5 ACTIVE FORMAT CHANGE SETTING ACCEPTED
- 2026-04-23T09:45:05 F_CHANGE From: M06 To: M10 ID_D 2 ACTIVE FORMAT CHANGE REQUEST ACCEPTED
- 2026-04-13T11:34:15 F_CHANGE From: M10 To: M06 ID_D 5 ACTIVE FORMAT CHANGE SETTING ACCEPTED

## Bar Safety Focus
- `PRODUCT FLOW END` is expected low-product/waiting behavior and is not treated as root cause.
- `FILM FINISHED` is noisy/annoying context, but not the main concern for this investigation.
- `BAR SAFETY` is the priority alarm. On 2026-04-29 it appears at:
  - `10:10:03` active, `10:10:10` resolved
  - `10:13:17` active, `10:13:19` resolved
  - `10:13:22` active, `10:13:23` resolved
  - `10:21:06` active, `10:21:28` resolved
  - `10:23:27` active, `10:23:38` resolved
  - `10:27:38` active, `10:27:40` resolved
  - `10:28:00` active, `10:28:01` resolved
  - `10:31:03` active, `10:31:04` resolved
  - `10:36:09` active, `10:36:11` resolved
  - `10:36:18` active, `10:36:21` resolved
  - `10:36:29` active, `10:36:30` resolved
  - `12:08:07` active, `12:08:09` resolved
  - `12:08:16` active, `12:08:19` resolved
  - `12:08:26` active, `12:08:30` resolved
- Machine state transitions around these timestamps repeatedly show `SYSTEM RUNNING` dropping to `SYSTEM IN STOP`, sometimes cycling back to running within seconds.
- Parameter changes on 2026-04-28 were concentrated on `REEL_UP_BELT` acceleration/deceleration/frequency settings, not on 2026-04-29 before this export.

## Initial Read
- The most actionable pattern is repeated `BAR SAFETY` trips causing or coinciding with machine stop transitions.
- Next mechanical/electrical checks should focus on the bar safety chain and any seal-bar/B12/safety interlock that can briefly open during motion.
