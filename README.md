# AI Fault Detection Project

## Overview
This project is a proof-of-concept system to:
- Monitor an industrial machine using cameras
- Detect faults using AI
- Read machine data via Modbus TCP
- Provide alerts and recommendations

The first version uses simple rule-based detection and recommendation logic. As real fault codes are identified, the recommendation table can be expanded with machine-specific fixes.

## Development Approach
This workstation is for thinking, planning, documentation, lightweight code edits, and small simulated tests only.

Heavy workloads should run on the home system, including:
- AI model training
- YOLO or other camera inference against live video
- Long-running dashboard or data collection services
- Large video/image processing jobs
- Any stress testing or performance tuning

Repository for commits/uploads:
https://github.com/ArticWone/AI-Fault-Detection

## Current Project Status
Read the current factual timeline, diagnostic summary, and OEM support questions here:
[README_PROJECT_STATUS.md](README_PROJECT_STATUS.md)

## Known Faults and Fixes
Known faults, symptoms, fixes we tried, and fixes that worked are tracked in:
`docs/known-faults-and-fixes.md`

## Key Findings
- Machine: SMIPACK BP802ALV
- Supports Ethernet connection
- Supports Modbus TCP registers
- Remote access via VNC (UltraVNC)

## Next Steps
1. Connect to machine via Ethernet
2. Verify VNC connection
3. Read Modbus registers
4. Identify fault registers
5. Integrate camera AI

## Safety Note
AI system must NOT directly control emergency stop.
