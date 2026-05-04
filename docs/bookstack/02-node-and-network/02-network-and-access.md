# Network and Access

## Current Addresses

| Device | Address | Notes |
| --- | --- | --- |
| Node, machine side | `192.168.0.20` | Static Ethernet, main local access |
| Machine/HMI | `192.168.0.1` | Expected Modbus/VNC endpoint |
| Camera 1 | `192.168.0.25` | Reolink RLC-522 |
| Node Wi-Fi | `192.168.1.84` | Shop/home Wi-Fi side |
| Node Tailscale | `100.87.194.41` | Remote/admin access |

## LAN Ports

| Port | Purpose | Current intent |
| --- | --- | --- |
| `80/tcp` | Convenience proxy to Web UI | Open on `192.168.0.20` |
| `22/tcp` | SSH | Open on LAN/admin network |
| `8000/tcp` | SMI Web UI | Open on LAN |
| `6875/tcp` | BookStack | Open on LAN |
| `1880/tcp` | Node-RED | Installed, localhost-only by default |
| `1883/tcp` | MQTT | Installed, localhost-only by default |

## Tailscale

Tailscale is installed, enabled, and currently online. The Web UI Admin area can turn the Tailscale service on/off.

For IT firewall requests, allow:

- outbound `TCP 443`
- outbound `UDP 41641`
- outbound `UDP 3478`
- optional outbound `TCP 80`

Inbound `UDP 41641` can improve direct connections but is not required.
