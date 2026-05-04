# Services and Ports

| Service | Port | Purpose |
| --- | --- | --- |
| `smi-edge-monitor` | `8000` | Main Web UI/API |
| `smi-web-ui-proxy` | `80` | Proxy to Web UI for easy browser access |
| `bookstack` | `6875` | Documentation app |
| `go2rtc` | `1984`, `8554`, `8555` | Camera restream/WebRTC bridge |
| `smi-node-red` | `1880` | IoT flow builder, localhost-only by default |
| `mosquitto` | `1883` | MQTT broker, localhost-only by default |
| `tailscaled` | dynamic | Remote private network |

## Useful Commands

```bash
systemctl status smi-edge-monitor.service --no-pager
systemctl status smi-node-red.service --no-pager
systemctl status mosquitto.service --no-pager
sudo ufw status numbered
ss -ltnp
```
