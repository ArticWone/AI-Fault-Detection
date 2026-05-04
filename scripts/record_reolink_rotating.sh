#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${SMI_CAMERA_ENV:-/srv/smi-ai/config/cameras.env}"
CAMERA_ID=""
HOST=""
USER_NAME="${SMI_CAMERA_USER:-admin}"
PASSWORD="${SMI_CAMERA_PASSWORD:-}"
STREAM="${SMI_CAMERA_STREAM:-main}"
PORT="${SMI_CAMERA_RTSP_PORT:-554}"
PATH_PREFIX="${SMI_CAMERA_RTSP_PATH_PREFIX:-Preview_01_}"
VIDEO_ROOT="${SMI_VIDEO_ROOT:-/srv/smi-ai/video}"
BUDGET_GB="${SMI_VIDEO_BUDGET_GB:-400}"
SEGMENT_SECONDS="${SMI_VIDEO_SEGMENT_SECONDS:-1800}"
RECORD_AUDIO="${SMI_RECORD_AUDIO:-0}"
RECORD_FPS="${SMI_RECORD_FPS:-15}"
OUTPUT_EXTENSION="${SMI_VIDEO_EXTENSION:-mp4}"

usage() {
  cat <<'EOF'
Usage: bash scripts/record_reolink_rotating.sh [options]

Options:
  --camera ID          Camera id from SMI_CAMERAS, for example infeed
  --host IP            Camera IP address, overrides env camera lookup
  --user USER          Camera username, default: admin
  --password PASS      Camera password. Prefer SMI_CAMERA_PASSWORD instead.
  --stream main|sub    RTSP stream, default: main
  --budget-gb GB       Total video budget across all cameras, default: 400
  --segment-seconds N  Segment length, default: 1800
  --record-audio       Include camera audio if available, default: video only
  --fps N              Output recording FPS, default: 15
  -h, --help           Show this help
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
  BUDGET_GB="${SMI_VIDEO_BUDGET_GB:-${BUDGET_GB}}"
  SEGMENT_SECONDS="${SMI_VIDEO_SEGMENT_SECONDS:-${SEGMENT_SECONDS}}"
  RECORD_AUDIO="${SMI_RECORD_AUDIO:-${RECORD_AUDIO}}"
  RECORD_FPS="${SMI_RECORD_FPS:-${RECORD_FPS}}"
  OUTPUT_EXTENSION="${SMI_VIDEO_EXTENSION:-${OUTPUT_EXTENSION}}"
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
    --budget-gb)
      BUDGET_GB="${2:?Missing value for --budget-gb}"
      shift 2
      ;;
    --segment-seconds)
      SEGMENT_SECONDS="${2:?Missing value for --segment-seconds}"
      shift 2
      ;;
    --record-audio)
      RECORD_AUDIO=1
      shift
      ;;
    --fps)
      RECORD_FPS="${2:?Missing value for --fps}"
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
CAMERA_DIR="${VIDEO_ROOT}/${CAMERA_ID}"
RTSP_URL="rtsp://${USER_NAME}:${PASSWORD}@${HOST}:${PORT}/${PATH_PREFIX}${STREAM}"
BUDGET_BYTES=$((BUDGET_GB * 1024 * 1024 * 1024))

mkdir -p "${CAMERA_DIR}"

prune_video_budget() {
  local current_bytes
  current_bytes="$(du -sb "${VIDEO_ROOT}" 2>/dev/null | awk '{print $1}')"
  while [[ "${current_bytes}" -gt "${BUDGET_BYTES}" ]]; do
    local oldest
    oldest="$(find "${VIDEO_ROOT}" -type f \( -name '*.mkv' -o -name '*.mp4' \) -printf '%T@ %p\n' | sort -n | head -1 | cut -d' ' -f2-)"
    if [[ -z "${oldest}" ]]; then
      break
    fi
    echo "Pruning old video: ${oldest}"
    rm -f -- "${oldest}"
    current_bytes="$(du -sb "${VIDEO_ROOT}" 2>/dev/null | awk '{print $1}')"
  done
}

echo "Recording ${CAMERA_ID} from ${HOST} ${STREAM} stream."
echo "Output: ${CAMERA_DIR}"
echo "Budget: ${BUDGET_GB}GB across ${VIDEO_ROOT}"
echo "Segment length: ${SEGMENT_SECONDS}s"
echo "Audio recording: ${RECORD_AUDIO}"
echo "Output FPS: ${RECORD_FPS}"

while true; do
  prune_video_budget
  DAY_DIR="${CAMERA_DIR}/$(date +%Y%m%d)"
  mkdir -p "${DAY_DIR}"

  map_args=(-map 0:v:0 -an)
  if [[ "${RECORD_AUDIO}" == "1" ]]; then
    map_args=(-map 0:v:0 -map 0:a?)
  fi

  ffmpeg -hide_banner -loglevel info \
    -rtsp_transport tcp \
    -i "${RTSP_URL}" \
    "${map_args[@]}" \
    -vf "fps=${RECORD_FPS},setpts=N/(${RECORD_FPS}*TB)" \
    -c:v libx264 \
    -preset ultrafast \
    -crf 23 \
    -pix_fmt yuv420p \
    -c:a aac \
    -avoid_negative_ts make_zero \
    -f segment \
    -segment_time "${SEGMENT_SECONDS}" \
    -segment_format "${OUTPUT_EXTENSION}" \
    -reset_timestamps 1 \
    -strftime 1 \
    "${DAY_DIR}/${CAMERA_ID}_%Y%m%d_%H%M%S.${OUTPUT_EXTENSION}" || true

  echo "ffmpeg exited for ${CAMERA_ID}; retrying in 5 seconds..."
  sleep 5
done
