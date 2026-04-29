#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
SIMULATE=0

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${REPO_DIR}/.venv/bin/python"

usage() {
  cat <<'EOF'
Usage: bash scripts/start_edge_monitor.sh [options]

Options:
  --simulate     Use generated machine data instead of Modbus TCP
  --host HOST    Web server host, default: 0.0.0.0
  --port PORT    Web server port, default: 8000
  -h, --help     Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --simulate)
      SIMULATE=1
      shift
      ;;
    --host)
      HOST="${2:?Missing value for --host}"
      shift 2
      ;;
    --port)
      PORT="${2:?Missing value for --port}"
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

if [[ ! -x "${PYTHON}" ]]; then
  PYTHON="python3"
fi

ARGS=(--host "${HOST}" --port "${PORT}")
if [[ "${SIMULATE}" -eq 1 ]]; then
  ARGS+=(--simulate)
fi

cd "${REPO_DIR}"
exec "${PYTHON}" -m edge_monitor.server "${ARGS[@]}"
