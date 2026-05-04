# System Architecture

## Hardware

- Node PC: Lenovo ThinkCentre M715q class thin client.
- Boot drive: 256GB NVMe, Ubuntu Server.
- Data/video drive: 512GB SSD mounted at `/srv/smi-ai`.
- Camera: Reolink RLC-522 at `192.168.0.25`.
- AI hardware: Coral Dual Edge TPU card installed; currently one TPU is visible to Linux as `/dev/apex_0`.

## Data Flow

1. Machine/HMI network provides Modbus and VNC from `192.168.0.1`.
2. Edge monitor reads Modbus and serves the Web UI on port `8000`.
3. go2rtc bridges RTSP camera video into WebRTC preview.
4. Recorder writes rotating video to `/srv/smi-ai/video`.
5. BookStack stores operator/process documentation on port `6875`.
6. Node-RED and MQTT are installed for future IoT flows and remain localhost-only unless opened from Admin.

## Persistent Paths

| Path | Purpose |
| --- | --- |
| `/srv/smi-ai/video` | Camera recordings |
| `/srv/smi-ai/camera_snapshots` | Camera snapshots |
| `/srv/smi-ai/hmi_snapshots` | HMI snapshots |
| `/srv/smi-ai/config` | Private runtime configs and API tokens |
| `/srv/smi-ai/bookstack` | BookStack Docker data |
