# Codex Task Prompt

You are given `m715q_bios_capture_codex.json`, a structured BIOS/hardware baseline for a Lenovo ThinkCentre M715q machine-learning/mapping proof-of-concept node.

Tasks:
1. Validate the JSON structure and normalize field names if needed.
2. Create a reusable schema for BIOS state captures across multiple nodes.
3. Identify fields useful for:
   - configuration drift detection
   - hardware fingerprinting
   - boot/security posture analysis
   - thermal/power behavior modeling
   - runtime telemetry correlation
4. Suggest a Linux/Unraid collector script that pairs this static BIOS state with live runtime data.
5. Keep all unknown or not-expanded BIOS submenu values as explicit null/unknown states, not assumptions.

Important:
- Do not overwrite captured values unless clearly marked as inferred.
- Preserve the original static BIOS snapshot.
- Treat this node as a proof-of-concept machine-learning diagnostics node.
