# Edge Monitor App

The edge monitor is a basic web app for the M715q thin client.

## What It Does

- polls the SMIPACK machine through the existing Modbus client
- stores recent samples in memory
- writes detector events through the existing event logger
- exposes JSON API endpoints
- shows a mobile-friendly browser dashboard
- embeds an HMI web viewer when the VNC bridge is running

## Folder Layout

- `app/`: shared machine logic
- `edge_monitor/`: web app and API
- `scripts/start_edge_monitor.sh`: starts the dashboard/API
- `scripts/start_hmi_web_viewer.sh`: starts the noVNC bridge for the HMI display

## API Endpoints

- `/api/current`: current machine status and latest sample
- `/api/history`: recent in-memory samples
- `/api/events`: recent detector events
- `/api/config`: machine/web viewer settings

## Test With Simulated Data

```bash
bash scripts/start_edge_monitor.sh --simulate
```

Open:

```text
http://SERVER_IP:8000
```

## Run Against The Machine

```bash
bash scripts/start_edge_monitor.sh
```

The Modbus target comes from `app/config.py`.

## HMI Viewer

The HMI viewer uses noVNC because browsers cannot connect directly to VNC.

Start it separately:

```bash
bash scripts/start_hmi_web_viewer.sh
```

Default bridge:

- HMI VNC target: `192.168.0.1:5900`
- browser port: `6080`

The dashboard at port `8000` embeds the noVNC page from port `6080`.

## First Version Limitations

- history is in memory and resets when the app restarts
- HMI viewing depends on VNC being enabled and reachable
- VNC authentication may still be required by the HMI
- the HMI viewer should stay local-network only
- this is monitor-first, not machine control
