#!/usr/bin/env python3
"""Remove duplicate BookStack pages by name inside a chapter, keeping newest."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = os.environ.get("BOOKSTACK_BASE_URL", "http://192.168.0.20:6875/api")
ENV_PATH = Path(os.environ.get("BOOKSTACK_ENV", "/srv/smi-ai/config/bookstack-api.env"))
PAYLOAD_PATH = Path(os.environ.get("BOOKSTACK_BP802ALV_PAYLOAD", "/tmp/bookstack_bp802alv_grouped.json"))
BOOK_NAME = "SMI Machine Documentation"
CHAPTER_NAME = "BP802ALV Clean Manual - Grouped"


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
        with urllib.request.urlopen(req, timeout=120) as response:
            body = response.read()
            return json.loads(body.decode("utf-8")) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


def token() -> str:
    env = read_env(ENV_PATH)
    return f"{env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}"


def find_book(auth: str) -> dict:
    for book in request("GET", "/books", auth).get("data", []):
        if book.get("name") == BOOK_NAME:
            return book
    raise RuntimeError(f"Book not found: {BOOK_NAME}")


def find_chapter(auth: str, book_id: int) -> dict:
    contents = request("GET", f"/books/{book_id}", auth)
    for item in contents.get("contents", []):
        if item.get("type") == "chapter" and item.get("name") == CHAPTER_NAME:
            return item
    raise RuntimeError(f"Chapter not found: {CHAPTER_NAME}")


def chapter_pages(auth: str, chapter_id: int) -> list[dict]:
    chapter = request("GET", f"/chapters/{chapter_id}", auth)
    return chapter.get("pages", [])


def main() -> None:
    auth = token()
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    expected_names = {
        page["name"]
        for chapter in payload["chapters"]
        for page in chapter["pages"]
    }

    book = find_book(auth)
    chapter = find_chapter(auth, int(book["id"]))
    pages_by_name: dict[str, list[dict]] = {}
    for page in chapter_pages(auth, int(chapter["id"])):
        if page.get("name") in expected_names:
            pages_by_name.setdefault(page["name"], []).append(page)

    deleted = 0
    for name, pages in sorted(pages_by_name.items()):
        pages.sort(key=lambda page: int(page["id"]), reverse=True)
        keep = pages[0]
        for page in pages[1:]:
            request("DELETE", f"/pages/{page['id']}", auth)
            deleted += 1
            print(f"deleted duplicate {page['id']}: {name}; kept {keep['id']}")
    print(f"deleted {deleted} duplicate pages")


if __name__ == "__main__":
    main()
