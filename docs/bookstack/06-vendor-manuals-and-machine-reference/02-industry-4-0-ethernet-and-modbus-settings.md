# Industry 4.0 Ethernet and Modbus Settings

Source PDF: `docs/vendor-documents/smipack/DM200289_D_Industry_4_0_Ethernet_Modbus.pdf`

Manual code: `DM200289`

Revision: `D2`

## Purpose

This document describes Ethernet access between the machine/operator panel and a PC, including VNC access and Modbus register interaction.

## Machine Network Settings

| Setting | Value used for this project |
| --- | --- |
| Machine/HMI IP | `192.168.0.1` |
| Subnet mask | `255.255.255.0` |
| Node machine-side IP | `192.168.0.20` |
| Modbus TCP port | `502` |
| VNC port | `5900` |

The manual points to the operator panel menu:

`Utility -> Network`

Use a static IP when possible so the machine address does not change after restart.

## VNC Access

The manual describes using UltraVNC Viewer to connect to the machine IP.

Project use:

- The Web UI shows the HMI/VNC display.
- Keep VNC access limited to the machine-side/internal network.
- Avoid exposing VNC directly through Tailscale or broad LAN rules unless explicitly approved.

## Modbus Registers From Manual

| Register | Manual meaning | Current project use |
| --- | --- | --- |
| `13300` | Format currently in use | Read current format |
| `10142` | Set/requested format | Read or controlled write only with approval |
| `10112` | Production lot ID | Read lot number |
| `10161` | Number of packages to be wrapped | Read package count / count target candidate |

## Write Safety

The manual includes write examples for `10142`, `10112`, and `10161`.

Project rule:

- Use read-only Modbus checks while mapping.
- Do not write registers or request format changes unless the machine owner approves the exact action.
- Any future write control must require an operator confirmation step and be logged.

## Search Terms

- Industry 4.0
- Ethernet interface
- operator panel
- touch-screen ARM
- VNC
- UltraVNC
- Modbus TCP
- Ananas
- register 13300
- register 10142
- register 10112
- register 10161
