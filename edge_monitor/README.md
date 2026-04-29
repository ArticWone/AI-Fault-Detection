# Edge Monitor

This folder contains the thin-client web app for the M715q edge box.

It intentionally stays separate from the core machine logic:

- `app/`: Modbus client, detector, config, event logging, simulated machine data
- `edge_monitor/`: web dashboard, API, and HMI browser viewer integration
- `scripts/`: setup and launch scripts
- `docs/`: setup notes and project references

## Run With Simulated Data

```bash
python -m edge_monitor.server --simulate --host 0.0.0.0 --port 8000
```

Then open:

```text
http://SERVER_IP:8000
```

## Run Against The Machine

```bash
python -m edge_monitor.server --host 0.0.0.0 --port 8000
```

The server reads the machine using the shared config in `app/config.py`.

## HMI Web Viewer

The dashboard includes an HMI panel, but the VNC bridge must be started separately:

```bash
bash scripts/start_hmi_web_viewer.sh
```

The bridge downloads noVNC into `tools/noVNC` inside this repository the first time it runs.
