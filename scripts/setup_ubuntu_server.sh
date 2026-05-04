#!/usr/bin/env bash
set -euo pipefail

INSTALL_CODEX=1
INSTALL_DOCKER=0
INSTALL_CORAL=0
DATA_ROOT="/srv/smi-ai"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: sudo bash scripts/setup_ubuntu_server.sh [options]

Options:
  --skip-codex       Do not install Node.js/Codex CLI
  --install-docker   Install Docker Engine from Ubuntu packages
  --install-coral    Attempt Coral PCIe driver/runtime install
  --data-root PATH   Runtime data directory, default: /srv/smi-ai
  -h, --help         Show this help

Run this from the cloned AI-Fault-Detection repository on Ubuntu Server.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-codex)
      INSTALL_CODEX=0
      shift
      ;;
    --install-docker)
      INSTALL_DOCKER=1
      shift
      ;;
    --install-coral)
      INSTALL_CORAL=1
      shift
      ;;
    --data-root)
      DATA_ROOT="${2:?Missing value for --data-root}"
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

if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run with sudo: sudo bash scripts/setup_ubuntu_server.sh" >&2
  exit 1
fi

PROJECT_USER="${SUDO_USER:-$(logname 2>/dev/null || echo root)}"

echo "==> Updating Ubuntu packages"
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

echo "==> Installing base packages"
DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  curl \
  build-essential \
  dkms \
  efibootmgr \
  ffmpeg \
  git \
  gnupg \
  htop \
  iproute2 \
  iputils-ping \
  lm-sensors \
  lsb-release \
  net-tools \
  nmap \
  nvme-cli \
  openssh-server \
  pciutils \
  pkg-config \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv \
  rsync \
  smartmontools \
  software-properties-common \
  unzip \
  usbutils \
  v4l-utils

if apt-cache show "linux-headers-$(uname -r)" >/dev/null 2>&1; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y "linux-headers-$(uname -r)"
else
  echo "Warning: linux headers for $(uname -r) were not found in apt cache."
fi

PYTHON_VENV_PACKAGE="$(python3 -c 'import sys; print(f"python{sys.version_info.major}.{sys.version_info.minor}-venv")')"
if apt-cache show "${PYTHON_VENV_PACKAGE}" >/dev/null 2>&1; then
  DEBIAN_FRONTEND=noninteractive apt-get install -y "${PYTHON_VENV_PACKAGE}"
fi

echo "==> Enabling SSH"
systemctl enable --now ssh

echo "==> Creating runtime directories at ${DATA_ROOT}"
install -d -m 775 -o "${PROJECT_USER}" -g "${PROJECT_USER}" \
  "${DATA_ROOT}" \
  "${DATA_ROOT}/config" \
  "${DATA_ROOT}/data" \
  "${DATA_ROOT}/hmi_snapshots" \
  "${DATA_ROOT}/logs" \
  "${DATA_ROOT}/models" \
  "${DATA_ROOT}/video"

echo "==> Creating Python virtual environment in ${REPO_DIR}/.venv"
sudo -u "${PROJECT_USER}" python3 -m venv "${REPO_DIR}/.venv"
sudo -u "${PROJECT_USER}" "${REPO_DIR}/.venv/bin/python" -m pip install --upgrade pip setuptools wheel
if [[ -f "${REPO_DIR}/requirements.txt" ]]; then
  sudo -u "${PROJECT_USER}" "${REPO_DIR}/.venv/bin/pip" install -r "${REPO_DIR}/requirements.txt"
fi

if [[ "${INSTALL_CODEX}" -eq 1 ]]; then
  echo "==> Installing Node.js 22 and Codex CLI"
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
  DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
  npm install -g @openai/codex
  echo "Codex installed. Sign in later as ${PROJECT_USER} with: codex --login"
fi

if [[ "${INSTALL_DOCKER}" -eq 1 ]]; then
  echo "==> Installing Docker"
  DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose-v2
  systemctl enable --now docker
  usermod -aG docker "${PROJECT_USER}"
  echo "Docker installed. Log out and back in before running Docker as ${PROJECT_USER}."
fi

if [[ "${INSTALL_CORAL}" -eq 1 ]]; then
  echo "==> Installing Coral PCIe runtime and driver"
  install -d -m 755 /usr/share/keyrings
  curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    | gpg --dearmor -o /usr/share/keyrings/coral-edgetpu-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/coral-edgetpu-archive-keyring.gpg] https://packages.cloud.google.com/apt coral-edgetpu-stable main" \
    > /etc/apt/sources.list.d/coral-edgetpu.list
  apt-get update
  if ! DEBIAN_FRONTEND=noninteractive apt-get install -y gasket-dkms libedgetpu1-std; then
    echo "Warning: Coral gasket-dkms install failed. Newer Ubuntu kernels may need a patched gasket driver."
  fi

  groupadd -f apex
  usermod -aG apex "${PROJECT_USER}"
  cat >/etc/udev/rules.d/65-apex.rules <<'EOF'
SUBSYSTEM=="apex", MODE="0660", GROUP="apex"
EOF
  udevadm control --reload-rules
  udevadm trigger || true
  echo "After reboot, check Coral with: lspci | grep -i apex && ls -l /dev/apex*"
fi

cat >"${DATA_ROOT}/README.txt" <<EOF
SMI AI runtime data folder.

Suggested usage:
- data: Modbus CSV logs and event data
- hmi_snapshots: HMI display snapshots captured through VNC
- logs: service logs and transcripts
- models: deployed model files
- video: camera captures and clips
EOF
chown "${PROJECT_USER}:${PROJECT_USER}" "${DATA_ROOT}/README.txt"

echo "==> Setup complete"
echo "Repo: ${REPO_DIR}"
echo "Data root: ${DATA_ROOT}"
echo "Project user: ${PROJECT_USER}"
echo
echo "Next checks:"
echo "  ${REPO_DIR}/.venv/bin/python -m app.main --simulate --once"
echo "  systemctl status ssh --no-pager"
echo "  lsblk"
if [[ "${INSTALL_CODEX}" -eq 1 ]]; then
  echo "  codex --login"
fi
