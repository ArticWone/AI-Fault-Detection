# Camera and Recording

## Camera

- Model: Reolink RLC-522
- Current IP: `192.168.0.25`
- Admin URL: `http://192.168.0.25/`
- RTSP port: `554`

## Streams

```text
rtsp://<user>:<password>@192.168.0.25:554/Preview_01_main
rtsp://<user>:<password>@192.168.0.25:554/Preview_01_sub
```

## Recording

- Video path: `/srv/smi-ai/video`
- Snapshots: `/srv/smi-ai/camera_snapshots`
- Default target: rotating segments, currently planned around 30-minute chunks.
- One camera around 6 Mbps gives roughly 6 days in a 400GB budget.

## Camera Settings Used For Stability

For preview robustness, prefer H.264 main profile, moderate bitrate, and lower FPS if network/video artifacts appear.
