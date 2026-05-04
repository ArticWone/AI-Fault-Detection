# Web UI and Admin Settings

The SMI Web UI is the local shop-floor dashboard. It shows machine connection status, camera preview, recordings, events, snapshots, and operator action buttons.

## Operator Controls

- **FAULT**: records a manual fault marker.
- **BAD PACK(S)**: captures a camera snapshot and logs a bad-pack event.
- **HMI Snapshot**: captures the HMI via VNC when reachable.
- **Camera Snapshot**: saves a camera still image.
- **Shutdown Node**: asks for confirmation, then shuts down the node.

## Settings

- Machine IP, Modbus port, connection timeout, poll rate.
- Live Modbus vs simulated mode.
- Tailscale on/off and status.
- Admin panel for Node-RED, MQTT, Tailscale, Wi-Fi, SSH command hints, and controlled LAN port exposure.

## Wi-Fi Admin

The Admin panel can scan Wi-Fi networks and write a controlled netplan Wi-Fi config. Passwords are not written into BookStack or git.
