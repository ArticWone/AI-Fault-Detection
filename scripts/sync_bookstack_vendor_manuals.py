#!/usr/bin/env python3
"""Sync searchable vendor manual notes into the local BookStack instance."""

from __future__ import annotations

import json
import os
import mimetypes
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = os.environ.get("BOOKSTACK_BASE_URL", "http://127.0.0.1:6875/api")
ENV_PATH = Path(os.environ.get("BOOKSTACK_ENV", "/srv/smi-ai/config/bookstack-api.env"))
BOOK_NAME = "SMI Machine Documentation"
CHAPTER_NAME = "Vendor Manuals and Machine Reference"
ATTACHMENT_DIR = Path(os.environ.get("BOOKSTACK_ATTACHMENT_DIR", "docs/vendor-documents/smipack"))


PAGES = [
    {
        "name": "SMIPACK BP802ALV 600R Manual - Search Index",
        "markdown": """# SMIPACK BP802ALV 600R Manual - Search Index

Source PDF: `DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf`

Manual code: `DM211643_S`

Machine: `BP802ALV 600R`

Description: Automatic overlap shrinkwrapper with in-line infeed.

## High-Value Search Terms

- BP802ALV 600R
- automatic overlap shrinkwrapper
- in-line infeed
- sealing bar
- film reel
- upper unwinder
- lower unwinder
- chain separator
- oven belt
- emergency door open
- bar safety
- film finishing
- film finished
- no pressure
- oven obstruction
- B11 obstruction
- B12 obstruction
- SQ13 problem
- inverter error
- I/O bus error

## Machine Areas To Map

| Area | Manual reference | Map use |
| --- | --- | --- |
| Infeed belt | Machine components and setup | Product entry and flow detection |
| Chain separator | Operation, alarms, inverter references | Pack spacing and obstruction faults |
| Sealing bar | Safety devices, maintenance, bar movement faults | Seal cycle, bar safety, sensor mapping |
| Film reels and unwinders | Film setup and film alarms | Film feed, reel end, tensioning |
| Oven / thermal chamber | Operation and temperature faults | Heat shrink, oven belt, PT100/temperature checks |
| Operator panel | Operation and alarms | HMI state, VNC view, operator prompts |

## Safety Devices And Sensors Mentioned

- Door magnetic sensors.
- Sealing bar sensors.
- Emergency mushroom button.
- Safety relay circuits.
- Tensioning bar sensors.
- Outfeed accumulation photocell.
- Obstruction photocell.
- Pressure switch.
- Oven temperature probe.
- Inverter/driver status signals.

## Alarm/Fault Phrases To Correlate

| Alarm phrase | Useful mapping target |
| --- | --- |
| `EMERGENCY DOOR OPEN` | Door interlocks and safety relay |
| `BAR SAFETY` | Sealing bar safety sensors and obstruction area |
| `FILM FINISHING` | Reel-end monitoring and film reserve |
| `FILM FINISHED` | Tensioning bar and reel-end sensors |
| `BAR MOVEMENT PROBLEM` | Bar position sensors, air pressure, solenoid valves |
| `OVEN OBSTRUCTION` | Outfeed/oven photocell timing |
| `CHAIN SEPARATOR OBSTRUCTION` | B11 sensor and chain separator path |
| `B12 OBSTRUCTION` | Sensor B12 near sealing bar |
| `NO PRESSURE` | Pneumatic supply and pressure switch |
| `ERROR I/O BUS 0` / `ERROR I/O BUS 1` | FLXIO module communication |

## Mapping Notes

Use this manual while filling in the machine parts and sensor map. Treat every physical sensor row as `candidate` until verified by both physical tracing and read-only data changes.
""",
    },
    {
        "name": "Industry 4.0 Ethernet and Modbus Settings",
        "markdown": """# Industry 4.0 Ethernet and Modbus Settings

Source PDF: `DM200289_D_Industry_4_0_Ethernet_Modbus.pdf`

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
""",
    },
    {
        "name": "External Reel-Holder Settings and Sensors",
        "markdown": """# External Reel-Holder Settings and Sensors

Source PDF: `DM200178_A_EN_external_reel_holder.pdf`

Manual code: `DM200178`

Revision: `A`

## Purpose

This manual covers the optional external reel-holder for bottom film loading.

## Main Components

| Manual item | Component |
| --- | --- |
| `1` | Reel-holder |
| `2` | Tensioning bar unit |
| `3` | Upper film return unit |
| `4` | Reel-holder motor |
| `5` | Tensioning bar sensor |
| `6` | Reel end photocell, when present |

## Electrical / Sensor References

| Label | Manual meaning | Mapping use |
| --- | --- | --- |
| `50.SQ.4` | Photocell for reel end control, if included | Film finished / reel end candidate |
| `51.B` | Sensor used to unwind film reel | Film feed / tensioning candidate |
| `32.M.1` | Reel-holder gearmotor | External reel-holder motor |

## Setup Notes

- The reel-holder can be installed on the left side or right side of the shrinkwrapper.
- Removed sheet metal guards must be reinstalled before use.
- Gearmotor rotation must match the direction shown in the manual.
- Film reel stops should leave a small clearance so film can drag correctly.
- Counterweights are only added if film unwinding has difficulty.

## Hazard Areas

| Zone | Risk |
| --- | --- |
| Zone A | Crushing risk during reel loading |
| Zone B | Entanglement/crushing risk around tensioning bars during film unwinding |

## Search Terms

- external reel-holder
- bottom loading
- tensioning bar
- reel-holder motor
- reel end photocell
- 50.SQ.4
- 51.B
- 32.M.1
- upper film return unit
- film unwinding
""",
    },
    {
        "name": "Wiring Diagrams - Part 1 Scan Index",
        "markdown": """# Wiring Diagrams - Part 1 Scan Index

Source PDF: `SMIPACK_wiring_diagrams_part_1_scan.pdf`

Drive title: `[Untitled].pdf`

Uploaded: `2026-05-04`

Status: Part 1 of the wiring diagrams. Part 2 is expected after the next scan.

## Purpose

This page makes the first scanned wiring diagram packet searchable in BookStack and gives us a place to record traced wires, sensors, terminals, pages, and cabinet references.

The PDF is an image scan, so text search inside the PDF may be limited until OCR is added.

## Search Terms

- wiring diagram
- electrical drawing
- schematic
- cabinet
- terminal
- terminal block
- wire number
- sensor cable
- I/O module
- FLXIO
- FLXMOD
- DIO 16
- TCP A3
- relay
- contactor
- safety relay
- emergency stop
- door interlock
- sealing bar
- B1
- B2
- B11
- B12
- SQ13
- 50.SQ.4
- 50.SQ.5
- 51.B
- 52.SQ.4
- 52.SQ.5
- 55.SQ.2
- 162.KM.8
- 162.KM.9
- 60.KA.3
- 32.M.1

## Trace Table

| Page/sheet | Wire/terminal | Device label | Device type | Machine area | Related register/fault | Status |
| --- | --- | --- | --- | --- | --- | --- |
| unknown | unknown | unknown | unknown | unknown | unknown | needs trace |

## Mapping Workflow

1. Identify each sheet/page number from the scan.
2. Record visible device labels such as `B12`, `SQ13`, `KM`, `KA`, `M`, and terminal numbers.
3. Match labels to the machine parts and sensor map.
4. Confirm with read-only Modbus values, HMI alarms, or camera evidence.
5. Mark each row as `candidate`, `verified`, or `retired`.

## Known Next Step

Add wiring diagrams part 2 after it is scanned on `2026-05-05`, then merge both packets into one trace index.
""",
    },
]


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def request(method: str, path: str, token: str, payload: dict | None = None) -> dict:
    data = None
    headers = {"Authorization": f"Token {token}", "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read()
            return json.loads(body.decode("utf-8")) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def multipart_request(method: str, path: str, token: str, fields: dict[str, str], file_path: Path) -> dict:
    boundary = "----smi-bookstack-boundary"
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        parts.append(str(value).encode("utf-8"))
        parts.append(b"\r\n")

    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8")
    )
    parts.append(file_path.read_bytes())
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))

    headers = {
        "Authorization": f"Token {token}",
        "Accept": "application/json",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    req = urllib.request.Request(f"{BASE_URL}{path}", data=b"".join(parts), headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read()
            return json.loads(body.decode("utf-8")) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def find_book(token: str) -> dict:
    data = request("GET", "/books", token)
    for book in data.get("data", []):
        if book.get("name") == BOOK_NAME:
            return book
    raise RuntimeError(f"Book not found: {BOOK_NAME}")


def get_book_detail(token: str, book_id: int) -> dict:
    return request("GET", f"/books/{book_id}", token)


def find_chapter(book_detail: dict) -> dict | None:
    for item in book_detail.get("contents", []):
        if item.get("type") == "chapter" and item.get("name") == CHAPTER_NAME:
            return item
    return None


def create_chapter(token: str, book_id: int) -> dict:
    return request(
        "POST",
        "/chapters",
        token,
        {
            "book_id": book_id,
            "name": CHAPTER_NAME,
            "description": "Searchable vendor manual notes, settings, and machine reference pages.",
        },
    )


def find_page(token: str, page_name: str) -> dict | None:
    data = request("GET", "/pages", token)
    for page in data.get("data", []):
        if page.get("name") == page_name:
            return page
    return None


def list_attachments(token: str) -> list[dict]:
    data = request("GET", "/attachments", token)
    return data.get("data", [])


def upsert_page(token: str, book_id: int, chapter_id: int, page: dict) -> str:
    existing = find_page(token, page["name"])
    payload = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "name": page["name"],
        "markdown": page["markdown"],
    }
    if existing:
        request("PUT", f"/pages/{existing['id']}", token, payload)
        return f"updated page {existing['id']}: {page['name']}"
    created = request("POST", "/pages", token, payload)
    return f"created page {created.get('id')}: {page['name']}"


def attach_file_to_page(token: str, page_name: str, file_name: str, attachment_name: str) -> str:
    page = find_page(token, page_name)
    if not page:
        raise RuntimeError(f"Page not found for attachment: {page_name}")
    page_id = int(page["id"])
    existing = list_attachments(token)
    for attachment in existing:
        attached_to = attachment.get("uploaded_to") or attachment.get("page_id")
        if attachment.get("name") == attachment_name and int(attached_to or 0) == page_id:
            return f"attachment already present on page {page_id}: {attachment_name}"

    file_path = ATTACHMENT_DIR / file_name
    if not file_path.exists():
        return f"attachment file missing, skipped: {file_path}"
    created = multipart_request(
        "POST",
        "/attachments",
        token,
        {"name": attachment_name, "uploaded_to": str(page_id)},
        file_path,
    )
    return f"created attachment {created.get('id')} on page {page_id}: {attachment_name}"


def main() -> None:
    env = read_env(ENV_PATH)
    token_id = env["BOOKSTACK_TOKEN_ID"]
    token_secret = env["BOOKSTACK_TOKEN_SECRET"]
    token = f"{token_id}:{token_secret}"
    book = find_book(token)
    book_id = int(book["id"])
    detail = get_book_detail(token, book_id)
    chapter = find_chapter(detail) or create_chapter(token, book_id)
    chapter_id = int(chapter["id"])
    print(f"book {book_id}: {BOOK_NAME}")
    print(f"chapter {chapter_id}: {CHAPTER_NAME}")
    for page in PAGES:
        print(upsert_page(token, book_id, chapter_id, page))
    attachments = [
        (
            "SMIPACK BP802ALV 600R Manual - Search Index",
            "DM211643-S_B_EN_BP802ALV_600R_use-maintenance.pdf",
            "SMIPACK BP802ALV 600R Use and Maintenance Manual.pdf",
        ),
        (
            "Industry 4.0 Ethernet and Modbus Settings",
            "DM200289_D_Industry_4_0_Ethernet_Modbus.pdf",
            "SMIPACK Industry 4.0 Ethernet and Modbus Manual.pdf",
        ),
        (
            "External Reel-Holder Settings and Sensors",
            "DM200178_A_EN_external_reel_holder.pdf",
            "SMIPACK External Reel-Holder Manual.pdf",
        ),
        (
            "Wiring Diagrams - Part 1 Scan Index",
            "SMIPACK_wiring_diagrams_part_1_scan.pdf",
            "SMIPACK Wiring Diagrams Part 1 Scan.pdf",
        ),
    ]
    for page_name, file_name, attachment_name in attachments:
        print(attach_file_to_page(token, page_name, file_name, attachment_name))


if __name__ == "__main__":
    main()
