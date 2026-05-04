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

## Temporary Debug Sudo

During setup/debug, the M715q may temporarily allow passwordless sudo for the `user` account through:

```text
/etc/sudoers.d/90-smi-ai-setup
```

This is convenient while installing packages and configuring services over SSH, but it should not remain enabled in the final deployment.

Remove before final setup/signoff:

```bash
sudo rm /etc/sudoers.d/90-smi-ai-setup
sudo -k
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

## Tailscale And Firewall Baseline

References:

- [Tailscale firewall compatibility and workarounds](https://tailscale.com/docs/integrations/firewalls#firewall-compatibility-and-workarounds)
- [Tailscale firewall ports FAQ](https://tailscale.com/docs/reference/faq/firewall-ports)

Tailscale usually works through normal firewalls by using NAT traversal, with DERP relay fallback when direct peer-to-peer traffic cannot be established. For this node, keep UFW enabled and only expose the services that are needed.

Baseline policy:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

Allow remote support and app services from Tailscale:

```bash
sudo ufw allow in on tailscale0 to any port 22 proto tcp
sudo ufw allow in on tailscale0 to any port 8000 proto tcp
sudo ufw allow in on tailscale0 to any port 1984 proto tcp
sudo ufw allow in on tailscale0 to any port 8554 proto tcp
sudo ufw allow in on tailscale0 to any port 8555
sudo ufw allow in on tailscale0 to any port 6080 proto tcp
```

Port purpose:

- `22/tcp`: SSH
- `8000/tcp`: SMI web UI
- `1984/tcp`: go2rtc web/API
- `8554/tcp`: RTSP restream
- `8555/tcp` and `8555/udp`: WebRTC
- `6080/tcp`: noVNC HMI viewer

The live LAN should not expose every service. Current setup intentionally allows the SMI web UI on the shop Wi-Fi/LAN so phones can reach the dashboard:

```bash
sudo ufw allow in on wlx6c4cbce74d9c to any port 8000 proto tcp
sudo ufw allow in on enp2s0f0 to any port 8000 proto tcp
```

Before the node goes onto a production network, add web UI authentication or limit this to Tailscale only.

If an upstream firewall is strict, ask IT for these outbound rules from the node:

- allow TCP outbound to `*:443`
- allow UDP outbound from source port `41641` to `*:*`
- allow UDP outbound to `*:3478`
- optional: allow TCP outbound to `*:80` for faster startup and captive-portal checks

If IT requires destination allowlisting instead of open outbound rules, prefer Tailscale domain rules over hardcoded IPs. At minimum, allow:

- `login.tailscale.com`
- `controlplane.tailscale.com`
- `log.tailscale.com`
- `console.tailscale.com`
- DERP relay hosts such as `derp1-all.tailscale.com` through the current DERP list

Opening inbound UDP `41641` to the node can improve direct peer-to-peer connections when both sides are behind difficult firewalls, but it is optional. Tailscale can still fall back to DERP relay over TCP `443`; that may be slower but should still work.

The setup hotspot uses the Wi-Fi adapter only when normal Wi-Fi is unavailable:

```bash
sudo ufw allow in on wlx6c4cbce74d9c to any port 80 proto tcp
sudo ufw allow in on wlx6c4cbce74d9c to any port 8080 proto tcp
sudo ufw allow in on wlx6c4cbce74d9c to any port 53
sudo ufw allow in on wlx6c4cbce74d9c to any port 67 proto udp
```

Verify after any firewall change:

```bash
sudo ufw enable
sudo ufw status verbose
tailscale status
```
