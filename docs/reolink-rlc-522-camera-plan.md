# Reolink RLC-522 Camera Plan

## Goal

Prepare the brain node for Reolink RLC-522 IP cameras without storing camera credentials in git.

The RLC-522 is a PoE H.264 camera with RTSP support. Reolink's RTSP format for a standalone camera is:

```text
rtsp://<username>:<password>@<ip-address>:554/Preview_01_main
rtsp://<username>:<password>@<ip-address>:554/Preview_01_sub
```

Older RLC-522 firmware may instead expose:

```text
rtsp://<username>:<password>@<ip-address>:554/h264Preview_01_main
rtsp://<username>:<password>@<ip-address>:554/h264Preview_01_sub
```

Use the main stream for evidence recording and the sub stream for low-cost monitoring or early AI experiments.

Official references:

- RLC-522 product/specs: https://reolink.com/us/product/rlc-522/
- Reolink RTSP format: https://support.reolink.com/articles/900000630706-Introduction-to-RTSP/

## Network Prep

Recommended camera network:

- Brain node: `192.168.0.20/24`
- Machine/HMI: `192.168.0.1`
- First camera: `192.168.0.25`
- Future cameras: reserve a small block such as `192.168.0.31-192.168.0.39`

Use DHCP reservations or static camera IPs so video filenames stay meaningful over time.

Suggested camera names:

- `camera1`
- `infeed`
- `sealbar`
- `discharge`

## Brain Node Runtime Config

Create a private config file on the brain node:

```bash
sudo mkdir -p /srv/smi-ai/config
sudo cp config/cameras.env.example /srv/smi-ai/config/cameras.env
sudo chown user:user /srv/smi-ai/config/cameras.env
chmod 600 /srv/smi-ai/config/cameras.env
nano /srv/smi-ai/config/cameras.env
```

Do not put the real password in this repository.

## Test A Camera

From the brain node repo:

```bash
bash scripts/test_reolink_camera.sh --camera camera1
```

Or without the env camera list:

```bash
SMI_CAMERA_PASSWORD='camera-password' bash scripts/test_reolink_camera.sh --host 192.168.0.25 --user smi --camera camera1
```

The script checks the RTSP port and captures one JPEG frame under:

```text
/srv/smi-ai/video/_snapshots/
```

## Start Rotating Recording

For one camera:

```bash
bash scripts/record_reolink_rotating.sh --camera camera1
```

For all cameras listed in `/srv/smi-ai/config/cameras.env`, run one process per camera:

```bash
for camera in camera1 infeed sealbar discharge; do
  nohup bash scripts/record_reolink_rotating.sh --camera "$camera" \
    >"/srv/smi-ai/logs/record_${camera}.log" 2>&1 &
done
```

Each camera writes five-minute segments by default:

```text
/srv/smi-ai/video/<camera-id>/YYYYMMDD/<camera-id>_YYYYMMDD_HHMMSS.mkv
```

The script prunes oldest video files when total video usage exceeds `SMI_VIDEO_BUDGET_GB`.

## One-Command Node Bring-Up

After `/srv/smi-ai/config/cameras.env` is filled in on the brain node, run:

```bash
bash scripts/bringup_node_stack.sh
```

The bring-up script:

- starts the main web UI/API if it is not already running
- confirms `/api/current` responds
- verifies the machine collector is receiving Modbus samples
- tests each camera listed in `SMI_CAMERAS`
- starts rotating recording for each reachable camera
- confirms non-empty `.mkv` video files are being written

Use this lighter check when you only want to test cameras without starting recording:

```bash
bash scripts/bringup_node_stack.sh --no-recording
```

## Storage Planning

The RLC-522 main stream default bitrate is roughly 6 Mbps. With a 400GB rotating budget:

- One camera at 6 Mbps: about 6 days.
- Two cameras at 6 Mbps each: about 3 days.
- Three cameras at 6 Mbps each: about 2 days.

For longer retention, use lower bitrate, lower FPS, sub stream, motion-triggered recording, or event-only clip extraction.
