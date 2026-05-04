#!/usr/bin/env bash
set -euo pipefail

IFACE="${SMI_WIFI_IFACE:-wlx6c4cbce74d9c}"
SSID="${SMI_SETUP_SSID:-SMI-Node-Setup}"
PASSPHRASE="${SMI_SETUP_PASSPHRASE:-}"
AP_ADDR="${SMI_SETUP_ADDR:-192.168.50.1}"
RUN_DIR="/run/smi-wifi-setup"
PORTAL="${SMI_SETUP_PORTAL:-/usr/local/sbin/smi-wifi-setup-portal}"
NETPLAN_PATH="${SMI_WIFI_NETPLAN:-/etc/netplan/10-wifi-live.yaml}"
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=1; shift ;;
    --if-needed) FORCE=0; shift ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

wifi_online() {
  ip -4 addr show dev "${IFACE}" | grep -q ' inet ' &&
    ip route | grep -q "default .* dev ${IFACE}"
}

if [[ "${FORCE}" -ne 1 ]] && wifi_online; then
  exit 0
fi

if [[ -z "${PASSPHRASE}" ]]; then
  if [[ -f /etc/smi-wifi-setup.env ]]; then
    # shellcheck disable=SC1091
    source /etc/smi-wifi-setup.env
  fi
fi

if [[ -z "${PASSPHRASE}" || "${#PASSPHRASE}" -lt 8 ]]; then
  echo "Missing SMI_SETUP_PASSPHRASE, minimum 8 characters." >&2
  exit 1
fi

mkdir -p "${RUN_DIR}"
chmod 700 "${RUN_DIR}"

systemctl stop "netplan-wpa-${IFACE}.service" 2>/dev/null || true
systemctl stop wpa_supplicant.service 2>/dev/null || true
pkill -F "${RUN_DIR}/dnsmasq.pid" 2>/dev/null || true
pkill -F "${RUN_DIR}/hostapd.pid" 2>/dev/null || true

ip addr flush dev "${IFACE}" || true
ip link set "${IFACE}" up
ip addr add "${AP_ADDR}/24" dev "${IFACE}"

cat >"${RUN_DIR}/hostapd.conf" <<EOF
interface=${IFACE}
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=6
wmm_enabled=1
auth_algs=1
wpa=2
wpa_passphrase=${PASSPHRASE}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

cat >"${RUN_DIR}/dnsmasq.conf" <<EOF
interface=${IFACE}
bind-interfaces
dhcp-range=192.168.50.20,192.168.50.80,255.255.255.0,1h
dhcp-option=3,${AP_ADDR}
dhcp-option=6,${AP_ADDR}
address=/#/${AP_ADDR}
log-facility=-
EOF

hostapd -B -P "${RUN_DIR}/hostapd.pid" "${RUN_DIR}/hostapd.conf"
dnsmasq --conf-file="${RUN_DIR}/dnsmasq.conf" --pid-file="${RUN_DIR}/dnsmasq.pid"

export SMI_WIFI_IFACE="${IFACE}"
export SMI_WIFI_NETPLAN="${NETPLAN_PATH}"
export SMI_HOSTAPD_PID="${RUN_DIR}/hostapd.pid"
export SMI_DNSMASQ_PID="${RUN_DIR}/dnsmasq.pid"
exec "${PORTAL}"
