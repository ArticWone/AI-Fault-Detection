#!/usr/bin/env bash
set -euo pipefail

chmod 755 /usr/local/sbin/smi-wifi-setup-portal /usr/local/sbin/smi-wifi-setup-hotspot

if [[ ! -f /etc/smi-wifi-setup.env ]]; then
  pass="$(python3 - <<'PY'
import secrets
import string

alphabet = string.ascii_letters + string.digits
print("".join(secrets.choice(alphabet) for _ in range(16)))
PY
)"
  printf 'SMI_SETUP_PASSPHRASE=%s\n' "${pass}" > /etc/smi-wifi-setup.env
  chmod 600 /etc/smi-wifi-setup.env
fi

cat >/etc/systemd/system/smi-wifi-setup.service <<'EOF'
[Unit]
Description=SMI temporary Wi-Fi setup hotspot when normal Wi-Fi is unavailable
After=systemd-networkd.service
Wants=systemd-networkd.service

[Service]
Type=simple
EnvironmentFile=-/etc/smi-wifi-setup.env
ExecStart=/usr/local/sbin/smi-wifi-setup-hotspot --if-needed
Restart=no

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable smi-wifi-setup.service

ufw allow in on wlx6c4cbce74d9c to any port 8080 proto tcp comment 'SMI WiFi setup portal'
ufw allow in on wlx6c4cbce74d9c to any port 80 proto tcp comment 'SMI WiFi setup captive portal'
ufw allow in on wlx6c4cbce74d9c to any port 53 comment 'SMI WiFi setup DNS'
ufw allow in on wlx6c4cbce74d9c to any port 67 proto udp comment 'SMI WiFi setup DHCP'

/usr/local/sbin/smi-wifi-setup-hotspot --if-needed

echo "SETUP_SSID=SMI-Node-Setup"
sed -n 's/^SMI_SETUP_PASSPHRASE=/SETUP_PASSWORD=/p' /etc/smi-wifi-setup.env
systemctl is-enabled smi-wifi-setup.service
ufw status verbose
