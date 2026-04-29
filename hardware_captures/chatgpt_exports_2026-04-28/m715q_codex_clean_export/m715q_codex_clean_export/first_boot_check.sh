#!/usr/bin/env bash
set -euo pipefail
echo "=== M715q First Boot Check ==="
if [ -d /sys/firmware/efi ]; then echo "UEFI boot confirmed"; else echo "WARNING: Legacy/CSM boot detected"; fi
command -v efibootmgr >/dev/null 2>&1 && sudo efibootmgr || echo "Install efibootmgr: sudo apt install efibootmgr"
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,PARTTYPE,MODEL
lscpu | grep -E 'Model name|CPU\(s\)|Thread|Core|Socket|MHz' || true
free -h
ip -br addr
