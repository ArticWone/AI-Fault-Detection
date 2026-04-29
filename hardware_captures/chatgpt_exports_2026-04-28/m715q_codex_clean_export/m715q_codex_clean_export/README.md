# M715q Codex Clean Export

Clean handoff package for the Lenovo ThinkCentre M715q AI/edge-monitor node.

## Current target

- Ubuntu Server
- GPT boot disk
- UEFI/non-CSM target
- Secure Boot disabled
- Secure Boot Status: Setup Mode
- Featured server snaps: skipped

## Repo context

Last known commit: `7575485` — `Add M715q setup notes and edge monitor`

## Important captured failure

The machine previously showed:

```text
Could not create MokListRT: Volume Full
Something has gone seriously wrong: import_mok_state() failed: Volume Full
```

Secure Boot keys were cleared and the system now shows:

```text
Secure Boot Status: Setup Mode
Secure Boot: Disabled
```

If the error persists, clean stale UEFI boot entries with `efibootmgr`.

## First boot baseline

```bash
sudo apt update
sudo apt install -y openssh-server git curl python3 python3-venv python3-pip build-essential
```
