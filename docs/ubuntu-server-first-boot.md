# Ubuntu Server First Boot

Use this after installing Ubuntu Server on the ThinkCentre M715q.

## Recommended Install

- Install Ubuntu Server LTS on the 256GB NVMe.
- Enable OpenSSH during install.
- Keep the 512GB SATA SSD unformatted until after the system boots and you can confirm the disk name with `lsblk`.
- Use a normal admin user account, not direct root login.

## Clone The Project

```bash
git clone https://github.com/ArticWone/AI-Fault-Detection.git ~/AI-Fault-Detection
cd ~/AI-Fault-Detection
```

## Run First-Boot Setup

Base install with Codex CLI:

```bash
sudo bash scripts/setup_ubuntu_server.sh
```

Base install plus Docker:

```bash
sudo bash scripts/setup_ubuntu_server.sh --install-docker
```

Base install plus Docker and Coral PCIe driver/runtime:

```bash
sudo bash scripts/setup_ubuntu_server.sh --install-docker --install-coral
```

Coral install is optional for the first boot. It is safer to run it after the Coral card is physically installed.

## Reboot

```bash
sudo reboot
```

## Verify After Reboot

Check Python simulation:

```bash
cd ~/AI-Fault-Detection
.venv/bin/python -m app.main --simulate --once
```

Check SSH:

```bash
systemctl status ssh --no-pager
```

Check disks:

```bash
lsblk
```

Run the project first-boot hardware check:

```bash
cd ~/AI-Fault-Detection
bash scripts/first_boot_check.sh
```

Check Codex:

```bash
codex --version
codex --login
```

Check the edge monitor dashboard with simulated data:

```bash
cd ~/AI-Fault-Detection
bash scripts/start_edge_monitor.sh --simulate
```

Then open:

```text
http://SERVER_IP:8000
```

Check Coral after the module is installed:

```bash
lspci | grep -i apex
lspci | grep -i coral
ls -l /dev/apex*
```

For the Dual Edge TPU, seeing two devices such as `/dev/apex_0` and `/dev/apex_1` would be ideal. Seeing only one device may mean the M.2 slot exposes only one PCIe lane or needs BIOS/kernel tuning.

## Mounting The 512GB SATA SSD

Do not blindly format disks. First identify the SATA SSD:

```bash
lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINTS
```

Once the correct disk is identified, create a filesystem and mount it at `/srv/smi-ai`. Record the UUID in `/etc/fstab` so it mounts at boot.

The setup script creates `/srv/smi-ai` and these folders:

- `/srv/smi-ai/data`
- `/srv/smi-ai/logs`
- `/srv/smi-ai/models`
- `/srv/smi-ai/video`

## Machine Network

The SMIPACK machine was previously found at:

- machine/HMI: `192.168.0.1`
- PC direct Ethernet: `192.168.0.10`
- Modbus TCP: port `502`
- VNC: port `5900`

Keep machine-network routing simple. If this PC also has internet access, use a separate interface for internet when possible.
