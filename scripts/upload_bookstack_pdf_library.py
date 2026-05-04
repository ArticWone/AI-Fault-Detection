#!/usr/bin/env python3
"""Upload searchable PDF library pages into BookStack."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = os.environ.get("BOOKSTACK_BASE_URL", "http://192.168.0.20:6875/api")
ENV_PATH = Path(os.environ.get("BOOKSTACK_ENV", "/srv/smi-ai/config/bookstack-api.env"))
PAYLOAD_PATH = Path(os.environ.get("BOOKSTACK_LIBRARY_PAYLOAD", "/tmp/bookstack_pdf_library_pages.json"))
BOOK_NAME = "SMI Machine Documentation"
CHAPTER_NAME = "Searchable PDF Library"


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


def get_token() -> str:
    env = read_env(ENV_PATH)
    return f"{env['BOOKSTACK_TOKEN_ID']}:{env['BOOKSTACK_TOKEN_SECRET']}"


def find_book(token: str) -> dict:
    data = request("GET", "/books", token)
    for book in data.get("data", []):
        if book.get("name") == BOOK_NAME:
            return book
    raise RuntimeError(f"Book not found: {BOOK_NAME}")


def get_book_detail(token: str, book_id: int) -> dict:
    return request("GET", f"/books/{book_id}", token)


def find_or_create_chapter(token: str, book_id: int) -> dict:
    detail = get_book_detail(token, book_id)
    for item in detail.get("contents", []):
        if item.get("type") == "chapter" and item.get("name") == CHAPTER_NAME:
            return item
    return request(
        "POST",
        "/chapters",
        token,
        {
            "book_id": book_id,
            "name": CHAPTER_NAME,
            "description": "Searchable text extracted from manuals and wiring scan index pages.",
        },
    )


def list_pages(token: str) -> list[dict]:
    data = request("GET", "/pages", token)
    return data.get("data", [])


def upsert_page(token: str, book_id: int, chapter_id: int, page: dict, existing_pages: dict[str, dict]) -> str:
    payload = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "name": page["name"],
        "markdown": page["markdown"],
    }
    existing = existing_pages.get(page["name"])
    if existing:
        request("PUT", f"/pages/{existing['id']}", token, payload)
        return f"updated {existing['id']}: {page['name']}"
    created = request("POST", "/pages", token, payload)
    return f"created {created.get('id')}: {page['name']}"


def main() -> None:
    token = get_token()
    book = find_book(token)
    book_id = int(book["id"])
    chapter = find_or_create_chapter(token, book_id)
    chapter_id = int(chapter["id"])
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    existing_pages = {page["name"]: page for page in list_pages(token)}
    print(f"book {book_id}: {BOOK_NAME}")
    print(f"chapter {chapter_id}: {CHAPTER_NAME}")
    for page in payload["pages"]:
        print(upsert_page(token, book_id, chapter_id, page, existing_pages))


if __name__ == "__main__":
    main()
