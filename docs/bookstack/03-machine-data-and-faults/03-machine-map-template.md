# Machine Parts and Sensor Map

Use this page as the working map while tracing the machine. The goal is to connect each physical part or sensor to its electrical I/O, Modbus value, camera view, and fault meaning.

## Mapping Rules

- Label the physical location first, then attach register details later.
- Prefer read-only checks while mapping.
- Record uncertainty instead of guessing. Use `unknown`, `candidate`, or `confirmed`.
- Add photos or camera snapshots when a part is hard to describe.
- Do not store passwords, vendor login credentials, or API tokens here.

## Machine Area Map

| Area | Physical location | Main parts | Sensors/actuators | Camera coverage | Notes |
| --- | --- | --- | --- | --- | --- |
| Infeed | unknown | unknown | unknown | unknown | Trace during walkdown |
| Film feed | unknown | unknown | Top film-feed candidate | Camera 1 candidate | Compare against register `10183` |
| Seal area | unknown | Seal bars candidate | Seal-bar candidates | Camera 1 candidate | Compare against `10325`, `13539` |
| Outfeed | unknown | unknown | Package count candidate | Camera 1 candidate | Compare against register `10161` |
| Safety / E-stop | unknown | E-stop circuit | Run-state candidate | unknown | Compare against `10167` |

## Sensor Trace Sheet

| ID | Name | Type | Physical location | Wire/terminal | I/O module | Modbus register | Normal value | Fault value | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S-001 | unknown | sensor | unknown | unknown | unknown | unknown | unknown | unknown | candidate |

## Actuator Trace Sheet

| ID | Name | Type | Physical location | Wire/terminal | I/O module | Control source | Safe test method | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-001 | unknown | actuator | unknown | unknown | unknown | unknown | observe only | candidate |

## Register-To-Part Candidates

| Register | Candidate part/function | How to verify | Current status |
| --- | --- | --- | --- |
| `10059` | Machine state / start-stop | Watch value while machine changes state | candidate |
| `10112` | Lot number | Compare to HMI lot number | known |
| `10142` | Set/requested format | Compare to HMI set format | known |
| `10161` | Package count | Compare to package counter | known |
| `10167` | E-stop/run-state standout | Watch during safe run/stop state changes | candidate |
| `10183` | Top film-feed | Watch while film feed moves | candidate |
| `10209` | Fault window | Compare during active fault | candidate |
| `10325` | Seal-bar candidate | Watch during seal cycle | candidate |
| `13300` | Current format | Compare to HMI current format | known |
| `13445` | B12 direct candidate | Trace from HMI/vendor docs | candidate |
| `13505` | B12 direct candidate | Trace from HMI/vendor docs | candidate |
| `13539` | Seal-bar or B12 secondary | Watch during seal cycle | candidate |

## Camera Correlation

| Camera | View | Parts visible | Useful for | Notes |
| --- | --- | --- | --- | --- |
| Camera 1 | Main test view | unknown | Bad pack snapshots, fault review | Needs final mounted position |

## Walkdown Checklist

- Photograph control cabinet labels and I/O modules.
- Photograph each sensor with its cable route or nearby label.
- Record machine area, part name, and visible label.
- Trigger safe state changes and watch read-only Modbus values.
- Mark each row as `candidate` until verified by both physical trace and data change.
- Link any useful video segment or snapshot to the related part row.
