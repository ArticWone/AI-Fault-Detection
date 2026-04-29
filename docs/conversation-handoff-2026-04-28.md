# Conversation Handoff - 2026-04-28

## Hardware Plan

Target edge PC:
- Lenovo ThinkCentre M715q Tiny
- 256GB NVMe for Ubuntu Server and project code
- current 16GB RAM is enough for setup, Modbus logging, and dashboard testing
- planned 32GB RAM upgrade before heavier workloads
- planned 512GB SATA SSD for logs, camera captures, models, and datasets
- planned Google Coral M.2 Dual Edge TPU for lightweight edge inference

Recommendation:
- start the M715q now with 16GB RAM and the 256GB NVMe
- use it for Ubuntu setup, SSH, repo checkout, Modbus reads, register mapping, and early dashboard testing
- wait for the RAM/SSD/Coral upgrades before heavy camera AI, long video retention, or production-like service use

## OS Choice

Use Ubuntu Server LTS.

Reasons:
- stable headless Linux base
- good Python, Docker, SSH, camera, Modbus, and Coral tooling support
- lower overhead than Windows
- easier to run as an always-on edge box

Windows is only preferred if a required vendor tool or camera utility is Windows-only.

## Thin Client / Edge Monitor App

A basic web monitor was added under `edge_monitor/`.

It reuses shared project code from `app/`:
- Modbus client
- detector
- event logger
- simulator
- config

It provides:
- web dashboard at `/`
- `/api/current`
- `/api/history`
- `/api/events`
- `/api/config`

The first version keeps recent samples in memory and writes detector events through the existing CSV logger.

## HMI Web Viewer

Browsers cannot connect directly to VNC, so the HMI viewer uses noVNC/websockify as a bridge.

Default HMI target:
- `192.168.0.1:5900`

Default browser viewer:
- `http://SERVER_IP:6080/vnc.html`

The edge dashboard embeds the viewer from port `6080`.

Keep this local-network only and monitor-first. Machine control from a phone/app is a future safety-reviewed discussion, not part of the current plan.

## Packages To Install

The Ubuntu setup script installs:
- `ca-certificates`
- `curl`
- `dkms`
- `ffmpeg`
- `git`
- `gnupg`
- `htop`
- `iproute2`
- `iputils-ping`
- `lm-sensors`
- `lsb-release`
- `net-tools`
- `nmap`
- `openssh-server`
- `pciutils`
- `pkg-config`
- `python3`
- `python3-dev`
- `python3-pip`
- `python3-venv`
- `rsync`
- `software-properties-common`
- `unzip`
- `usbutils`
- `v4l-utils`
- matching Linux kernel headers when available

Python dependencies:
- `pymodbus`
- `fastapi`
- `uvicorn[standard]`

Optional:
- Docker via `--install-docker`
- Codex CLI through Node.js/npm
- Coral PCIe driver/runtime via `--install-coral` after the Coral is installed

## First Commands On The M715q

```bash
sudo apt update
sudo apt install -y git
git clone https://github.com/ArticWone/AI-Fault-Detection.git ~/AI-Fault-Detection
cd ~/AI-Fault-Detection
sudo bash scripts/setup_ubuntu_server.sh --install-docker
sudo reboot
```

Test with simulated data:

```bash
cd ~/AI-Fault-Detection
bash scripts/start_edge_monitor.sh --simulate
```

Open:

```text
http://SERVER_IP:8000
```

Start the HMI web viewer:

```bash
bash scripts/start_hmi_web_viewer.sh
```

## Safety Direction

The Android/mobile idea should start as read-only machine information:
- status
- faults
- package count
- format/lot
- camera/HMI view
- event history
- recommendations

Do not add machine control until there is vendor documentation, permission, safety review, and explicit physical safeguards.
