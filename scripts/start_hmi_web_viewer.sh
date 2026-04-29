#!/usr/bin/env bash
set -euo pipefail

HMI_HOST="${HMI_HOST:-192.168.0.1}"
HMI_VNC_PORT="${HMI_VNC_PORT:-5900}"
HMI_WEB_PORT="${HMI_WEB_PORT:-6080}"

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="${REPO_DIR}/tools"
NOVNC_DIR="${TOOLS_DIR}/noVNC"
WEBSOCKIFY_DIR="${NOVNC_DIR}/utils/websockify"

usage() {
  cat <<'EOF'
Usage: bash scripts/start_hmi_web_viewer.sh [options]

Options:
  --hmi-host HOST     HMI VNC host, default: 192.168.0.1
  --vnc-port PORT     HMI VNC port, default: 5900
  --web-port PORT     Browser viewer port, default: 6080
  -h, --help          Show this help

This starts noVNC inside tools/noVNC and bridges the browser viewer to the HMI VNC server.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --hmi-host)
      HMI_HOST="${2:?Missing value for --hmi-host}"
      shift 2
      ;;
    --vnc-port)
      HMI_VNC_PORT="${2:?Missing value for --vnc-port}"
      shift 2
      ;;
    --web-port)
      HMI_WEB_PORT="${2:?Missing value for --web-port}"
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

install_novnc() {
  mkdir -p "${TOOLS_DIR}"
  if [[ ! -d "${NOVNC_DIR}/.git" ]]; then
    git clone https://github.com/novnc/noVNC.git "${NOVNC_DIR}"
  fi

  if [[ ! -d "${WEBSOCKIFY_DIR}/.git" ]]; then
    git clone https://github.com/novnc/websockify.git "${WEBSOCKIFY_DIR}"
  fi
}

install_novnc

echo "Starting HMI web viewer"
echo "  HMI VNC: ${HMI_HOST}:${HMI_VNC_PORT}"
echo "  Browser: http://$(hostname -I | awk '{print $1}'):${HMI_WEB_PORT}/vnc.html?autoconnect=1&resize=remote&reconnect=1"
echo

exec "${NOVNC_DIR}/utils/novnc_proxy" \
  --listen "${HMI_WEB_PORT}" \
  --vnc "${HMI_HOST}:${HMI_VNC_PORT}"
