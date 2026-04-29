# M715q BIOS Baseline

Imported from the ChatGPT BIOS/export ZIPs on 2026-04-28.

This is a sanitized project summary. Raw hardware captures should stay in `hardware_captures/` and should not be committed because they may include MAC addresses, UUIDs, license IDs, disk serials, or other machine-specific identifiers.

## Machine

- Manufacturer: Lenovo
- Model: ThinkCentre M715q
- Platform: AMD Bristol Ridge
- CPU: AMD PRO A12-9800E, 4 cores
- Current memory: 16GB DDR4-2400
- Target memory: 32GB
- Current boot drive: 256GB WDC PC SN730 NVMe
- SATA drive: not detected during BIOS capture
- SATA mode: AHCI

## Firmware

- BIOS revision: `M11KT56A`
- BIOS date: `2022-12-16`
- Boot block revision: `1.56`
- Embedded controller: `M11CT11A`

## Target Boot Posture

- OS: Ubuntu Server
- Disk partition style: GPT
- Boot target: UEFI
- Secure Boot: Disabled
- Secure Boot status after key clear: Setup Mode
- Featured server snaps: skipped
- CSM: captured enabled, but target is UEFI-only/non-CSM once boot is stable

## Important BIOS Settings

- Onboard Ethernet: Enabled
- PXE option ROM: Enabled
- PXE IPv4 stack: Enabled
- PXE IPv6 stack: Enabled
- USB support: Enabled
- USB legacy support: Enabled
- SATA controller: Enabled
- Configure SATA as: AHCI
- After power loss: Last State
- Smart Power On: Enabled
- Cooling mode: Better Thermal Performance
- ICE thermal alert: Enabled
- DASH support: Disabled
- Device Guard: Disabled
- Chassis intrusion detection: Disabled

## Captured Failure Case

During Ubuntu boot/install work, the machine previously showed a UEFI/MOK variable failure:

```text
Could not create MokListRT: Volume Full
Could not create MokListXRT: Volume Full
Could not create SbatLevelRT: Volume Full
Could not create MokListTrustedRT: Volume Full
Something has gone seriously wrong: import_mok_state() failed: Volume Full
```

Current captured status:
- Secure Boot keys were cleared
- Secure Boot is disabled
- Secure Boot status is Setup Mode

If the error persists, boot a live Ubuntu environment and inspect stale boot entries with:

```bash
sudo efibootmgr
```

Remove only confirmed stale/duplicate entries:

```bash
sudo efibootmgr -b XXXX -B
```

## First-Boot Runtime Pairing

Pair this static BIOS baseline with Linux runtime telemetry:

```bash
lscpu
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,PARTTYPE,MODEL
lspci -nn
lsusb
ip -br addr
sensors
dmesg -T
journalctl -b
sudo smartctl -a /dev/DRIVE
sudo nvme smart-log /dev/nvme0
```

Use `scripts/first_boot_check.sh` for the lightweight first pass.

## Capture Limitations

- Some boot order submenus were not expanded.
- Some TPM/TCG, Secure Boot, event log, and automatic power-on submenus were not fully captured.
- Values were manually parsed from BIOS photos/exports.
- CSM was captured enabled, but the intended Ubuntu target is UEFI-only.
