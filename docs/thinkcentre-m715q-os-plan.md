# ThinkCentre M715q OS Plan

## Target Hardware
- PC: Lenovo ThinkCentre M715q Tiny
- Boot drive: 256GB NVMe SSD
- Data drive: 512GB SATA SSD
- Memory: 32GB DDR4 after upgrade
- AI accelerator: Google Coral M.2 Accelerator with Dual Edge TPU, pending arrival
- Network: wired Ethernet to the SMIPACK machine network

## Recommended OS
Use Ubuntu Server LTS on the 256GB NVMe boot drive.

Reasons:
- Stable headless server base for Python services, Modbus polling, camera capture, and dashboards.
- Good package support for Docker, Python, OpenSSH, VNC tooling, and industrial-network utilities.
- Easier long-term maintenance than a custom OS image at this stage.

Keep the first install simple:
- Install OpenSSH server.
- Use a static IP only on the machine-facing Ethernet network when the SMIPACK connection is ready.
- Keep the 512GB SATA SSD mounted separately for captured images, logs, model files, and long-running datasets.

## Suggested Disk Layout
256GB NVMe:
- `/`
- boot files
- application code
- Python virtual environments
- Docker packages/images if used

512GB SATA SSD:
- mount at `/srv/smi-ai`
- store runtime logs, camera captures, exports, and local datasets

Suggested folders:
- `/srv/smi-ai/data`
- `/srv/smi-ai/logs`
- `/srv/smi-ai/models`
- `/srv/smi-ai/video`

## First Boot Checklist
1. Update BIOS/firmware if Lenovo Vantage or Lenovo boot media shows updates.
2. Install Ubuntu Server LTS to the NVMe.
3. Enable OpenSSH during install.
4. Create the main project user.
5. Install base tools:
   - `git`
   - `python3-venv`
   - `python3-pip`
   - `curl`
   - `htop`
   - `lm-sensors`
   - `net-tools`
   - `nmap`
6. Clone this repository to `/opt/smi-ai/AI-Fault-Detection` or the user's home folder.
7. Create a Python virtual environment and install `requirements.txt`.
8. Mount the 512GB SATA SSD at `/srv/smi-ai`.
9. Confirm Ethernet connectivity to the machine network before running live Modbus tests.

## Coral Dual Edge TPU Notes
The M715q has separate M.2 slots for SSD and WLAN. The Coral Dual Edge TPU uses an M.2 E-key connector and needs PCIe access through the WLAN-style slot. Confirm the installed slot and BIOS behavior before depending on both TPUs.

After the Coral arrives:
1. Physically install the module in the WLAN M.2 slot.
2. Boot Linux and check PCIe detection:
   - `lspci | grep -i coral`
   - `lspci | grep -i apex`
3. Install the Coral PCIe driver and Edge TPU runtime.
4. Check device nodes:
   - `ls /dev/apex*`
5. For a dual TPU, verify whether one or two Apex devices appear.

If only one TPU appears, likely causes are:
- the M.2 slot exposes only one PCIe lane
- BIOS limitations
- PCIe power management
- driver/kernel compatibility

## Project Role
This PC should become the always-on edge box for:
- Modbus TCP polling
- event logging
- camera stream capture
- lightweight inference
- dashboard/API hosting

Avoid training large models on this machine. Keep model training and heavy experiments on a stronger workstation, then deploy optimized models here.

## Repo Gaps To Fix
The docs mention logger scripts and data-capture utilities that are not present in the current repository checkout:
- `app/cold_start_logger.py`
- `app/live_output_logger.py`
- `app/candidate_sensor_logger.py`
- `scripts/start_cold_start_log.ps1`
- `scripts/start_live_output_log.ps1`
- `scripts/start_candidate_sensor_log.ps1`
- `scripts/add_operator_marker.ps1`

Before the OS box becomes the main machine logger, either recover those files from the earlier workstation or rebuild them in this repo.
