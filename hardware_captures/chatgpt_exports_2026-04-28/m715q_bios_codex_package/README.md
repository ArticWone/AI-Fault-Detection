# Lenovo ThinkCentre M715q BIOS Capture Package

This package contains a structured BIOS/hardware baseline captured from BIOS screen photos.

## Files

- `m715q_bios_capture_codex.json`  
  Main Codex-ready structured export.

- `m715q_bios_capture_codex.yaml`  
  Human-readable mirror of the JSON export.

- `codex_prompt.md`  
  Suggested prompt to paste into Codex with this package.

## Notes

This is a high-confidence manual capture, but some nested BIOS submenus were not expanded yet:
- Primary/Automatic/Error boot sequences
- TCG/TPM feature setup
- Secure Boot details
- System Event Log
- Hard Disk Password
- Fingerprint Setup
- Automatic Power On submenu

Use this JSON as the static BIOS state vector and pair it later with Linux/Unraid runtime telemetry.
