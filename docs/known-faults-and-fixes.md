# Known Faults and Fixes

Use this file to record faults we have actually seen and the fixes that worked.
Keep entries practical: what happened, what we checked, what fixed it, and how confident we are.

## Status Key
- `suspected`: observed once, not confirmed yet
- `confirmed`: repeated or verified
- `resolved`: fix worked and machine returned to normal
- `monitoring`: fix was applied, but we are watching for repeat issues

## Fault Log
| Date | Fault or Symptom | Evidence | Likely Cause | Fix Attempted | Result | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TBD | Package count reset | Register `10161` dropped lower than previous value | Lot change, operator reset, restart, or register mapping issue | Confirm reset source on HMI and compare with operator action | Pending | suspected |

## Recommendation Rules To Add Later
Use this section when we discover a repeatable fix that should be moved into `app/recommendations.py`.

| Source | Condition | Recommended Fix |
| --- | --- | --- |
| `package_count` | `reset` | Confirm lot change, operator reset, or normal restart before treating as a fault. |

## Entry Template
```text
Date:
Fault or symptom:
Machine state:
Register values:
Camera observations:
Likely cause:
Fix attempted:
Result:
Status:
Notes:
```
