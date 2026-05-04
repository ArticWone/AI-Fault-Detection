# Security Boundaries

## What Is Intentionally Open

- SMI Web UI on LAN ports `80` and `8000`.
- SSH on approved/admin LAN.
- BookStack on LAN port `6875`.

## What Is Controlled

- Node-RED and MQTT default to localhost only.
- Admin panel can open/close selected LAN ports.
- Tailscale can be toggled from Settings/Admin.
- Wi-Fi can be scanned/changed from Admin using a limited helper.

## Secrets

Do not store passwords or tokens in BookStack pages or git. Runtime secrets live under `/srv/smi-ai/config` with restricted permissions.

## Machine Safety

The diagnostic stack must remain read-only toward the machine unless a future explicitly approved control project is defined. No emergency stop or safety circuit control belongs here.
