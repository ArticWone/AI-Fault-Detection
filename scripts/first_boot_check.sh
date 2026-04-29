#!/usr/bin/env bash
set -euo pipefail

echo "=== M715q First Boot Check ==="
echo

if [[ -d /sys/firmware/efi ]]; then
  echo "UEFI boot confirmed"
else
  echo "WARNING: Legacy/CSM boot detected"
fi

echo
echo "=== UEFI Boot Entries ==="
if command -v efibootmgr >/dev/null 2>&1; then
  sudo efibootmgr || true
else
  echo "Install efibootmgr: sudo apt install efibootmgr"
fi

echo
echo "=== Block Devices ==="
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,PARTTYPE,MODEL

echo
echo "=== CPU ==="
lscpu | grep -E 'Model name|CPU\(s\)|Thread|Core|Socket|MHz' || true

echo
echo "=== Memory ==="
free -h

echo
echo "=== Network ==="
ip -br addr

echo
echo "=== PCI Devices ==="
lspci -nn

echo
echo "=== USB Devices ==="
lsusb

echo
echo "=== Sensors ==="
if command -v sensors >/dev/null 2>&1; then
  sensors || true
else
  echo "Install lm-sensors: sudo apt install lm-sensors"
fi

echo
echo "=== NVMe SMART ==="
if command -v nvme >/dev/null 2>&1 && [[ -e /dev/nvme0 ]]; then
  sudo nvme smart-log /dev/nvme0 || true
else
  echo "NVMe tools/device not available yet"
fi
