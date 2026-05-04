#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${SMI_CAMERA_ENV:-/srv/smi-ai/config/cameras.env}"
LOG_ROOT="${SMI_LOG_ROOT:-/srv/smi-ai/logs}"
VIDEO_ROOT="${SMI_VIDEO_ROOT:-/srv/smi-ai/video}"
DATA_ROOT="${SMI_AI_DATA_ROOT:-/srv/smi-ai}"
WEB_HOST="${SMI_WEB_HOST:-0.0.0.0}"
WEB_PORT="${SMI_WEB_PORT:-8000}"
WEB_URL="${SMI_WEB_URL:-http://127.0.0.1:${WEB_PORT}}"
MACHINE_HOST="${SMI_MACHINE_IP:-192.168.0.1}"
MACHINE_PORT="${SMI_MACHINE_PORT:-502}"
MACHINE_CONNECT_TIMEOUT="${SMI_MACHINE_CONNECT_TIMEOUT:-120}"
START_RECORDING=1
START_HMI_VIEWER=0
SIMULATE=0
STATUS=0

usage() {
  cat <<'EOF'
Usage: bash scripts/bringup_node_stack.sh [options]

Starts and verifies the node runtime:
  1. main web UI/API
  2. machine data collector
  3. Reolink camera RTSP access
  4. rotating video recording

Options:
  --simulate              Start the web UI with simulated machine data
  --hmi-viewer            Also start the noVNC HMI web viewer
  --no-recording          Test cameras but do not start rotating recording
  --web-port PORT         Web UI port, default: 8000
  --machine-host HOST     Machine IP, default: 192.168.0.1
  --machine-port PORT     Machine Modbus TCP port, default: 502
  --machine-timeout SEC   Seconds to wait for machine connection, default: 120
  --env-file PATH         Camera env file, default: /srv/smi-ai/config/cameras.env
  -h, --help              Show this help

Camera credentials should live in the env file or process environment, not in git.
EOF
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  STATUS=1
  printf '[%s] WARN: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

fail() {
  printf '[%s] ERROR: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --simulate)
      SIMULATE=1
      shift
      ;;
    --hmi-viewer)
      START_HMI_VIEWER=1
      shift
      ;;
    --no-recording)
      START_RECORDING=0
      shift
      ;;
    --web-port)
      WEB_PORT="${2:?Missing value for --web-port}"
      WEB_URL="http://127.0.0.1:${WEB_PORT}"
      shift 2
      ;;
    --machine-host)
      MACHINE_HOST="${2:?Missing value for --machine-host}"
      export SMI_MACHINE_IP="${MACHINE_HOST}"
      shift 2
      ;;
    --machine-port)
      MACHINE_PORT="${2:?Missing value for --machine-port}"
      export SMI_MACHINE_PORT="${MACHINE_PORT}"
      shift 2
      ;;
    --machine-timeout)
      MACHINE_CONNECT_TIMEOUT="${2:?Missing value for --machine-timeout}"
      shift 2
      ;;
    --env-file)
      ENV_FILE="${2:?Missing value for --env-file}"
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

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
else
  warn "Camera env file not found: ${ENV_FILE}"
fi

SMI_VIDEO_ROOT="${SMI_VIDEO_ROOT:-${VIDEO_ROOT}}"
SMI_CAMERAS="${SMI_CAMERAS:-}"
SMI_EVENT_LOG_PATH="${SMI_EVENT_LOG_PATH:-${DATA_ROOT}/data/events.csv}"
export SMI_AI_DATA_ROOT="${DATA_ROOT}"
export SMI_VIDEO_ROOT
export SMI_EVENT_LOG_PATH

mkdir -p "${LOG_ROOT}" "${SMI_VIDEO_ROOT}" "${DATA_ROOT}" "$(dirname "${SMI_EVENT_LOG_PATH}")"

require_command() {
  command -v "$1" >/dev/null || fail "Missing required command: $1"
}

port_is_open() {
  local host="$1"
  local port="$2"
  timeout 2 bash -c "cat < /dev/null > /dev/tcp/${host}/${port}" >/dev/null 2>&1
}

wait_for_machine_connection() {
  if [[ "${SIMULATE}" -eq 1 ]]; then
    log "Simulated mode enabled; skipping machine connection wait."
    return
  fi

  local deadline=$((SECONDS + MACHINE_CONNECT_TIMEOUT))
  local next_notice="${SECONDS}"

  log "Waiting up to ${MACHINE_CONNECT_TIMEOUT}s for machine ${MACHINE_HOST}:${MACHINE_PORT}"
  until port_is_open "${MACHINE_HOST}" "${MACHINE_PORT}"; do
    if [[ "${SECONDS}" -ge "${deadline}" ]]; then
      warn "Machine ${MACHINE_HOST}:${MACHINE_PORT} did not connect within ${MACHINE_CONNECT_TIMEOUT}s. Check Ethernet, machine power, IP settings, and Modbus port."
      return 1
    fi

    if [[ "${SECONDS}" -ge "${next_notice}" ]]; then
      log "Machine not reachable yet at ${MACHINE_HOST}:${MACHINE_PORT}; still waiting."
      next_notice=$((SECONDS + 15))
    fi
    sleep 2
  done

  log "Machine connection verified at ${MACHINE_HOST}:${MACHINE_PORT}"
}

start_web_ui() {
  if port_is_open 127.0.0.1 "${WEB_PORT}"; then
    log "Web UI already listening on ${WEB_URL}"
    return
  fi

  local args=(--host "${WEB_HOST}" --port "${WEB_PORT}")
  if [[ "${SIMULATE}" -eq 1 ]]; then
    args+=(--simulate)
  fi

  log "Starting main web UI on ${WEB_HOST}:${WEB_PORT}"
  nohup bash "${REPO_DIR}/scripts/start_edge_monitor.sh" "${args[@]}" \
    >"${LOG_ROOT}/edge_monitor.log" 2>&1 &
}

start_hmi_viewer() {
  if [[ "${START_HMI_VIEWER}" -ne 1 ]]; then
    return
  fi

  local hmi_web_port="${HMI_WEB_PORT:-6080}"
  if port_is_open 127.0.0.1 "${hmi_web_port}"; then
    log "HMI web viewer already listening on port ${hmi_web_port}"
    return
  fi

  log "Starting HMI web viewer on port ${hmi_web_port}"
  nohup bash "${REPO_DIR}/scripts/start_hmi_web_viewer.sh" \
    >"${LOG_ROOT}/hmi_web_viewer.log" 2>&1 &
}

wait_for_web_api() {
  local deadline=$((SECONDS + 45))
  until curl -fsS "${WEB_URL}/api/current" >/dev/null; do
    if [[ "${SECONDS}" -ge "${deadline}" ]]; then
      tail -40 "${LOG_ROOT}/edge_monitor.log" 2>/dev/null || true
      fail "Web API did not become ready at ${WEB_URL}/api/current"
    fi
    sleep 1
  done
  log "Web API is responding: ${WEB_URL}/api/current"
}

check_machine_collector() {
  local payload
  payload="$(curl -fsS "${WEB_URL}/api/current")" || fail "Could not read web API current status"

  if ! PAYLOAD="${payload}" EXPECT_SIMULATED="${SIMULATE}" python3 - <<'PY'
import json
import os
import sys

payload = json.loads(os.environ["PAYLOAD"])
expect_simulated = os.environ.get("EXPECT_SIMULATED") == "1"
status = payload.get("status", {})
sample = payload.get("sample")
source = status.get("source")

print(f"Machine source: {source}")
print(f"Machine connected: {status.get('connected')}")
print(f"Last update: {status.get('last_update')}")
if status.get("last_error"):
    print(f"Last error: {status.get('last_error')}")

if not status.get("connected") or sample is None:
    sys.exit(3)

if not expect_simulated and source != "modbus":
    print("Machine is not using live Modbus data.")
    sys.exit(3)

values = sample.get("values", {})
print(f"Machine registers read: {len(values)}")
if values:
    preview = ", ".join(f"{key}={value}" for key, value in list(values.items())[:6])
    print(f"Latest values: {preview}")
PY
  then
    warn "Web UI is up, but machine data is not connected yet. Check Modbus network/HMI reachability."
    return
  fi

  log "Machine logs/data collector are active."
}

test_camera() {
  local camera_id="$1"
  local host="$2"

  log "Testing camera ${camera_id} at ${host}"
  if ! bash "${REPO_DIR}/scripts/test_reolink_camera.sh" --camera "${camera_id}" --host "${host}" \
    >"${LOG_ROOT}/camera_test_${camera_id}.log" 2>&1; then
    tail -40 "${LOG_ROOT}/camera_test_${camera_id}.log" 2>/dev/null || true
    warn "Camera ${camera_id} failed RTSP snapshot test."
    return 1
  fi

  tail -5 "${LOG_ROOT}/camera_test_${camera_id}.log" 2>/dev/null || true
  log "Camera ${camera_id} RTSP test passed."
}

recording_running() {
  local camera_id="$1"
  pgrep -af "record_reolink_rotating.sh .*--camera ${camera_id}" >/dev/null 2>&1
}

start_camera_recording() {
  local camera_id="$1"
  local host="$2"

  if [[ "${START_RECORDING}" -ne 1 ]]; then
    return
  fi

  if recording_running "${camera_id}"; then
    log "Recording already running for ${camera_id}"
    return
  fi

  log "Starting rotating recording for ${camera_id}"
  nohup bash "${REPO_DIR}/scripts/record_reolink_rotating.sh" --camera "${camera_id}" --host "${host}" \
    >"${LOG_ROOT}/record_${camera_id}.log" 2>&1 &
}

verify_recording_file() {
  local camera_id="$1"

  if [[ "${START_RECORDING}" -ne 1 ]]; then
    return
  fi

  local deadline=$((SECONDS + 30))
  local newest=""
  while [[ "${SECONDS}" -lt "${deadline}" ]]; do
    newest="$(find "${SMI_VIDEO_ROOT}/${camera_id}" -type f -name '*.mkv' -size +0c -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2- || true)"
    if [[ -n "${newest}" ]]; then
      log "Recording verified for ${camera_id}: ${newest}"
      return
    fi
    sleep 2
  done

  tail -40 "${LOG_ROOT}/record_${camera_id}.log" 2>/dev/null || true
  warn "No non-empty recording file appeared yet for ${camera_id}."
}

check_cameras() {
  if [[ -z "${SMI_CAMERAS}" ]]; then
    warn "No SMI_CAMERAS configured; camera tests skipped."
    return
  fi

  if [[ -z "${SMI_CAMERA_PASSWORD:-}" ]]; then
    warn "SMI_CAMERA_PASSWORD is not set; camera tests skipped."
    return
  fi

  local item camera_id host
  for item in ${SMI_CAMERAS}; do
    camera_id="${item%%=*}"
    host="${item#*=}"
    test_camera "${camera_id}" "${host}" || continue
    start_camera_recording "${camera_id}" "${host}"
    verify_recording_file "${camera_id}"
  done
}

main() {
  cd "${REPO_DIR}"

  require_command curl
  require_command python3
  require_command ffmpeg

  start_web_ui
  start_hmi_viewer
  wait_for_web_api
  wait_for_machine_connection || true
  check_machine_collector
  check_cameras

  log "Bring-up complete. Web UI: ${WEB_URL}"
  exit "${STATUS}"
}

main
