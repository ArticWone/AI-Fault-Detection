#!/usr/bin/env python3
"""Upload clean BP802ALV manual chapters into BookStack."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = os.environ.get("BOOKSTACK_BASE_URL", "http://192.168.0.20:6875/api")
ENV_PATH = Path(os.environ.get("BOOKSTACK_ENV", "/srv/smi-ai/config/bookstack-api.env"))
PAYLOAD_PATH = Path(os.environ.get("BOOKSTACK_BP802ALV_PAYLOAD", "/tmp/bookstack_bp802alv_chapters.json"))
BOOK_NAME = "SMI Machine Documentation"


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


def book_contents(auth: str, book_id: int) -> dict:
    return request("GET", f"/books/{book_id}", auth)


def find_or_create_chapter(auth: str, book_id: int, chapter: dict, existing: dict[str, dict]) -> dict:
    found = existing.get(chapter["name"])
    payload = {
        "book_id": book_id,
        "name": chapter["name"],
        "description": chapter.get("description", ""),
    }
    if found:
        request("PUT", f"/chapters/{found['id']}", auth, payload)
        return found
    return request("POST", "/chapters", auth, payload)


def page_index(auth: str) -> dict[str, dict]:
    return {page["name"]: page for page in request("GET", "/pages", auth).get("data", [])}


def upsert_page(auth: str, book_id: int, chapter_id: int, page: dict, existing_pages: dict[str, dict]) -> str:
    payload = {
        "book_id": book_id,
        "chapter_id": chapter_id,
        "name": page["name"],
        "markdown": page["markdown"],
    }
    existing = existing_pages.get(page["name"])
    if existing:
        request("PUT", f"/pages/{existing['id']}", auth, payload)
        return f"updated {existing['id']}: {page['name']}"
    created = request("POST", "/pages", auth, payload)
    return f"created {created.get('id')}: {page['name']}"


def main() -> None:
    auth = token()
    book = find_book(auth)
    book_id = int(book["id"])
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    contents = book_contents(auth, book_id)
    existing_chapters = {
        item["name"]: item
        for item in contents.get("contents", [])
        if item.get("type") == "chapter"
    }
    existing_pages = page_index(auth)
    print(f"book {book_id}: {BOOK_NAME}")
    for chapter in payload["chapters"]:
        created_chapter = find_or_create_chapter(auth, book_id, chapter, existing_chapters)
        chapter_id = int(created_chapter["id"])
        print(f"chapter {chapter_id}: {chapter['name']}")
        for page in chapter["pages"]:
            print("  " + upsert_page(auth, book_id, chapter_id, page, existing_pages))


if __name__ == "__main__":
    main()
