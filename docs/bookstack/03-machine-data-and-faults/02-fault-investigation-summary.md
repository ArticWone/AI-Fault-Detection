# Fault Investigation Summary

## Primary Issue

Recurring seal bar / BAR SAFETY related stops and bad packs after changeover from 20 oz bottles to 10 oz bottles.

## Working Theory

Evidence points toward instability or timing mismatch in the B1/B2/B12/seal-bar safety sequence rather than one simple failed sensor.

## Important Findings

- B1 and B2 were clarified as a tied pair, with B2 acting as the slave.
- B1/B2 sensors were replaced with SICK PN `1040752`.
- B2 could not simply be bypassed by unplugging; unplugging caused fault behavior.
- A B2 bracket was corrected to a true 90-degree position, reducing but not eliminating faults.
- HMI alarm history repeatedly shows BAR SAFETY paired with machine stop transitions.
- Candidate Modbus changes often occur within seconds, sometimes fractions of a second, of BAR SAFETY timestamps.

## Next Evidence To Capture

1. Machine connected to node at `192.168.0.1`.
2. Modbus log active with operator markers.
3. Camera recording/snapshots during the fault window.
4. HMI alarm/state export after a test run.
