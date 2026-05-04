# Operations: Startup, Shutdown, Recovery

## Normal Startup Check

```bash
cd ~/AI-Fault-Detection
bash scripts/bringup_node_stack.sh
```

## Bench/No-Machine Test

```bash
bash scripts/bringup_node_stack.sh --simulate
```

## Shutdown

Use the Web UI Shutdown Node button, or SSH:

```bash
sudo shutdown -h now
```

## After Reboot Verify

```bash
systemctl is-active smi-edge-monitor.service
systemctl is-active smi-web-ui-proxy.service
systemctl is-active tailscaled.service
systemctl is-active go2rtc.service
ss -ltnp
```

## If Web UI Is Down

```bash
sudo systemctl restart smi-edge-monitor.service
journalctl -u smi-edge-monitor.service -n 80 --no-pager
```
