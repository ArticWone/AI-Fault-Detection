# Edge Monitor App

The edge monitor is a basic web app for the M715q thin client.

## What It Does

- polls the SMIPACK machine through the existing Modbus client
- stores recent samples in memory
- writes detector events through the existing event logger
- exposes JSON API endpoints
- shows a mobile-friendly browser dashboard
- embeds an HMI web viewer when the VNC bridge is running
- captures HMI snapshots through VNC and exposes download links from the dashboard

## Folder Layout

- `app/`: shared machine logic
- `edge_monitor/`: web app and API
- `scripts/start_edge_monitor.sh`: starts the dashboard/API
- `scripts/start_hmi_web_viewer.sh`: starts the noVNC bridge for the HMI display

## API Endpoints

- `/api/current`: current machine status and latest sample
- `/api/history`: recent in-memory samples
- `/api/events`: recent detector events
- `/api/snapshots`: saved HMI snapshots
- `/api/config`: machine/web viewer settings

## Network Exposure

The dashboard runs on port `8000`. For test and shop-floor use, the node may allow this port from LAN and Tailscale. Before putting the node on a live internal network, keep UFW enabled, prefer Tailscale for remote access, and add web UI authentication before broad LAN exposure.

See the Tailscale firewall reference in [Ubuntu Server First Boot](ubuntu-server-first-boot.md#tailscale-and-firewall-baseline).

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

For the normal node startup path, prefer the full bring-up script:

```bash
bash scripts/bringup_node_stack.sh
```

It starts the web UI if needed, checks `/api/current`, verifies that machine samples are coming in, writes event logs under `/srv/smi-ai/data/events.csv` by default, tests configured IP cameras, and starts/validates rotating recording.

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

## HMI Snapshots

The dashboard has a Snapshot button beside the HMI display header. Browser security blocks direct screenshots of the noVNC iframe, so the backend captures from the HMI VNC server with `vncdotool`.

Default snapshot folder:

```text
/srv/smi-ai/hmi_snapshots
```

The dashboard shows the latest 3 snapshots, includes a View more option, and provides download links that work from the device viewing the site.

If the HMI VNC server requires a password, set it before starting the edge monitor:

```bash
export SMI_HMI_VNC_PASSWORD='password_here'
bash scripts/start_edge_monitor.sh
```

## First Version Limitations

- history is in memory and resets when the app restarts
- HMI viewing depends on VNC being enabled and reachable
- VNC authentication may still be required by the HMI
- the HMI viewer should stay local-network only
- this is monitor-first, not machine control
