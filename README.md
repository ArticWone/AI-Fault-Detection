# AI Fault Detection Project

Generated: 2026-04-27 16:21:56.449263

## Overview
This project is a proof-of-concept system to:
- Monitor an industrial machine using cameras
- Detect faults using AI
- Read machine data via Modbus TCP
- Provide alerts and recommendations

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
