#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SMI_CAMERA_ENV:-/srv/smi-ai/config/cameras.env}"
CAMERA_ID=""
HOST=""
USER_NAME="${SMI_CAMERA_USER:-admin}"
PASSWORD="${SMI_CAMERA_PASSWORD:-}"
STREAM="${SMI_CAMERA_STREAM:-main}"
PORT="${SMI_CAMERA_RTSP_PORT:-554}"
PATH_PREFIX="${SMI_CAMERA_RTSP_PATH_PREFIX:-Preview_01_}"
VIDEO_ROOT="${SMI_VIDEO_ROOT:-/srv/smi-ai/video}"

usage() {
  cat <<'EOF'
Usage: bash scripts/test_reolink_camera.sh [options]

Options:
  --camera ID       Camera id from SMI_CAMERAS, for example infeed
  --host IP         Camera IP address, overrides env camera lookup
  --user USER       Camera username, default: admin
  --password PASS   Camera password. Prefer SMI_CAMERA_PASSWORD instead.
  --stream main|sub RTSP stream, default: main
  -h, --help        Show this help
EOF
}

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  USER_NAME="${SMI_CAMERA_USER:-${USER_NAME}}"
  PASSWORD="${SMI_CAMERA_PASSWORD:-${PASSWORD}}"
  STREAM="${SMI_CAMERA_STREAM:-${STREAM}}"
  PORT="${SMI_CAMERA_RTSP_PORT:-${PORT}}"
  PATH_PREFIX="${SMI_CAMERA_RTSP_PATH_PREFIX:-${PATH_PREFIX}}"
  VIDEO_ROOT="${SMI_VIDEO_ROOT:-${VIDEO_ROOT}}"
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --camera)
      CAMERA_ID="${2:?Missing value for --camera}"
      shift 2
      ;;
    --host)
      HOST="${2:?Missing value for --host}"
      shift 2
      ;;
    --user)
      USER_NAME="${2:?Missing value for --user}"
      shift 2
      ;;
    --password)
      PASSWORD="${2:?Missing value for --password}"
      shift 2
      ;;
    --stream)
      STREAM="${2:?Missing value for --stream}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

lookup_camera_host() {
  local id="$1"
  local item
  for item in ${SMI_CAMERAS:-}; do
    if [[ "${item%%=*}" == "${id}" ]]; then
      echo "${item#*=}"
      return 0
    fi
  done
  return 1
}

if [[ -z "${HOST}" && -n "${CAMERA_ID}" ]]; then
  HOST="$(lookup_camera_host "${CAMERA_ID}")" || {
    echo "Camera '${CAMERA_ID}' not found in SMI_CAMERAS." >&2
    exit 1
  }
fi

if [[ -z "${HOST}" ]]; then
  echo "Missing camera host. Use --host IP or --camera ID." >&2
  exit 1
fi

if [[ -z "${PASSWORD}" ]]; then
  echo "Missing camera password. Set SMI_CAMERA_PASSWORD or pass --password." >&2
  exit 1
fi

if [[ "${STREAM}" != "main" && "${STREAM}" != "sub" ]]; then
  echo "--stream must be main or sub." >&2
  exit 1
fi

command -v ffmpeg >/dev/null || {
  echo "ffmpeg is required. Run scripts/setup_ubuntu_server.sh on the brain node." >&2
  exit 1
}

CAMERA_ID="${CAMERA_ID:-camera_${HOST//./_}}"
SNAPSHOT_DIR="${VIDEO_ROOT}/_snapshots"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUTPUT="${SNAPSHOT_DIR}/${CAMERA_ID}_${STREAM}_${TIMESTAMP}.jpg"
RTSP_URL="rtsp://${USER_NAME}:${PASSWORD}@${HOST}:${PORT}/${PATH_PREFIX}${STREAM}"

mkdir -p "${SNAPSHOT_DIR}"

echo "Checking RTSP port ${HOST}:${PORT}..."
timeout 5 bash -c "cat < /dev/null > /dev/tcp/${HOST}/${PORT}" || {
  echo "Could not connect to ${HOST}:${PORT}." >&2
  exit 1
}

echo "Capturing one frame from ${CAMERA_ID} ${STREAM} stream..."
ffmpeg -hide_banner -loglevel warning \
  -rtsp_transport tcp \
  -i "${RTSP_URL}" \
  -frames:v 1 \
  -y "${OUTPUT}"

echo "Snapshot saved: ${OUTPUT}"
