# Consolidation Notes - 2026-04-29

This branch combines the M715q edge-box handoff with the current SMI diagnostic findings so the next session can work from the whole project state.

## Included Branch Sources

- `codex/consolidation-2026-04-29`
  - M715q runtime handoff under `m715q_runtime_handoff_2026-04-29/`
  - M715q hardware capture exports under `hardware_captures/chatgpt_exports_2026-04-28/`
- `origin/codex/update-smi-findings-2026-04-29-clean`
  - Daily diagnostic log for 2026-04-29
  - OEM-facing report amendment
  - I/O map starter
  - Machine export summaries
  - Focused BAR SAFETY / Modbus correlation notes
- `origin/codex/full-data-upload-2026-04-29`
  - Raw live-output runs
  - Machine exports
  - VNC screenshots
  - Manual renders
  - Photos, videos, and contact sheets
- `origin/known-faults-and-fixes`
  - Known-faults log
  - First-pass recommendation table used by the rule-based detector

## Start Here Tomorrow

1. Read `docs/daily-log-2026-04-29.md`.
2. Read `docs/oem-machine-report-amendment-2026-04-29.md`.
3. Review the focused summaries:
   - `data/machine_exports/20260429_122132/summary.md`
   - `data/machine_exports/20260429_122132/bar_safety_modbus_correlation.md`
   - `data/live_outputs/20260429/131837/stop_sequence_132135_132220_summary.md`
   - `data/live_outputs/20260429/131837/bad_packs_132457_summary.md`
4. For M715q state, review `m715q_runtime_handoff_2026-04-29/`.
5. For the beginning of repeatable fixes, review `docs/known-faults-and-fixes.md`.

## Current Diagnostic Direction

- Main live fault target: BAR SAFETY / B1-B2 / B12 / seal-bar safety chain.
- Strong Modbus candidates:
  - `10325`, `13539`: seal-bar or B12 secondary position.
  - `10168`, `10182`: B1/B2 tied pair or B2 group.
  - `13445`, `13505`: B12 direct candidates.
- Keep only one Modbus logger connected at a time.
- Use the WebUI fault marker once per event when practical.

## Intentionally Excluded

Private SSH keys are not committed to GitHub. The M715q private key and other local-only sensitive material remain in the encrypted local handoff folder:

```text
C:\Users\Jared\Desktop\SMI_AI_secure_handoff_2026-04-29
```

The password-protected archive is:

```text
C:\Users\Jared\Desktop\SMI_AI_secure_handoff_2026-04-29.7z
```

## Duplicate Handling

The full-data upload intentionally preserves raw run folders. Some run folders contain byte-identical `run.log` and `stdout.log` files, empty `stderr.log` placeholders, and repeated one-line CSV headers. These are retained as original capture artifacts, not treated as accidental branch duplicates.
