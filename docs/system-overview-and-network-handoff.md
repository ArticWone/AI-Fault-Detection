# SMI AI Node Handoff

## What This Is

The SMI AI node is a small Ubuntu computer connected to the SMIPACK machine area. It is being used to view machine status, show the HMI remotely, preview/record an IP camera, and prepare for AI fault detection.

This is a monitoring system. It should not control emergency stop or any safety-critical machine function.

## Current Hardware

- Node PC: Lenovo ThinkCentre M715q class thin client
- Boot drive: 256GB NVMe
- Data/video drive: 512GB SSD mounted at `/srv/smi-ai`
- Camera: Reolink RLC-522
- Planned AI hardware: Coral Dual Edge TPU

## Current Addresses

- Tailscale node IP: `100.87.194.41`
- Shop Wi-Fi/LAN node IP: `192.168.1.84`
- Machine/camera-side node IP: `192.168.0.20`
- Camera 1: `192.168.0.25`
- Machine/HMI: `192.168.0.1`

## What Is Running

| Service | Port | Purpose |
| --- | ---: | --- |
| SMI Web UI | `8000` | Main dashboard for phone/tablet/browser |
| SSH | `22` | Remote service/admin access |
| noVNC HMI viewer | `6080` | Browser view of machine HMI |
| go2rtc web/API | `1984` | Camera stream bridge |
| RTSP restream | `8554` | Camera restream |
| WebRTC | `8555` | Low-latency camera preview |

Main dashboard URLs:

- LAN: `http://192.168.1.84:8000`
- Tailscale: `http://100.87.194.41:8000`

## What The Dashboard Does Now

- shows latest machine sample/status
- can run in simulated mode when the machine is not connected
- shows the HMI display when noVNC is running
- shows the camera preview
- has HMI and camera snapshot buttons
- has operator buttons for `FAULT` and `BAD PACK(S)`
- has a shutdown button with a confirmation popup

## Camera And Recording

- Camera admin page: `http://192.168.0.25`
- RTSP camera access stays on the machine/camera network
- Video records to `/srv/smi-ai/video`
- Camera snapshots save to `/srv/smi-ai/camera_snapshots`
- Camera credentials should only live in `/srv/smi-ai/config/cameras.env`

The recording is a rotating buffer. About 400GB of video space gives roughly 6 days for one camera at about 6 Mbps.

## Normal Startup Check

From the node:

```bash
cd ~/AI-Fault-Detection
bash scripts/bringup_node_stack.sh
```

Without the machine connected:

```bash
bash scripts/bringup_node_stack.sh --simulate
```

This checks the web UI, machine data, camera access, and recording.

## IT Network Request

We want remote access through Tailscale and local dashboard access on the approved LAN.

Tailscale outbound access needed from the node:

- `TCP 443` outbound
- `UDP 41641` outbound
- `UDP 3478` outbound
- optional `TCP 80` outbound

Optional:

- inbound `UDP 41641` to the node can improve Tailscale direct connections, but it is not required.

If IT needs domain allowlisting:

- `login.tailscale.com`
- `controlplane.tailscale.com`
- `log.tailscale.com`
- `console.tailscale.com`
- Tailscale DERP relay hostnames

References:

- [Tailscale firewall ports FAQ](https://tailscale.com/docs/reference/faq/firewall-ports)
- [Tailscale firewall compatibility and workarounds](https://tailscale.com/docs/integrations/firewalls#firewall-compatibility-and-workarounds)

## Firewall Intent

UFW should stay enabled.

Allowed over Tailscale:

- SSH: `22`
- SMI Web UI: `8000`
- noVNC: `6080`
- go2rtc/camera services: `1984`, `8554`, `8555`

Allowed on normal LAN:

- SMI Web UI only: `8000`

Do not broadly expose SSH, noVNC, or camera streaming ports on the live company LAN unless IT approves it.
