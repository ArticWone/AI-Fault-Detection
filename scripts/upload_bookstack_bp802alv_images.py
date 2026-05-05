#!/usr/bin/env python3
"""Upload BP802ALV page images and insert them into grouped BookStack pages."""

from __future__ import annotations

import json
import mimetypes
import os
import re
import uuid
import urllib.error
import urllib.request
from pathlib import Path


BASE_URL = os.environ.get("BOOKSTACK_BASE_URL", "http://192.168.0.20:6875/api")
ENV_PATH = Path(os.environ.get("BOOKSTACK_ENV", "/srv/smi-ai/config/bookstack-api.env"))
PAYLOAD_PATH = Path(os.environ.get("BOOKSTACK_BP802ALV_PAYLOAD", "/tmp/bookstack_bp802alv_grouped.json"))
IMAGE_DIR = Path(os.environ.get("BOOKSTACK_BP802ALV_IMAGE_DIR", "/tmp/bp802alv_page_images"))
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


def multipart_request(path: str, token: str, fields: dict[str, str], files: dict[str, Path]) -> dict:
    boundary = f"----smi-bookstack-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        chunks.append(str(value).encode())
        chunks.append(b"\r\n")
    for name, file_path in files.items():
        filename = file_path.name
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        )
        chunks.append(f"Content-Type: {mime_type}\r\n\r\n".encode())
        chunks.append(file_path.read_bytes())
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=b"".join(chunks),
        headers={
            "Authorization": f"Token {token}",
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"POST {path} failed: {exc.code} {body}") from exc


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


def chapter_pages(auth: str, chapter_id: int) -> dict[str, dict]:
    chapter = request("GET", f"/chapters/{chapter_id}", auth)
    return {page["name"]: page for page in chapter.get("pages", [])}


def gallery_index(auth: str) -> dict[tuple[int, str], dict]:
    images: dict[tuple[int, str], dict] = {}
    offset = 0
    count = 500
    while True:
        response = request("GET", f"/image-gallery?count={count}&offset={offset}", auth)
        batch = response.get("data", [])
        for image in batch:
            uploaded_to = image.get("uploaded_to")
            if uploaded_to:
                images[(int(uploaded_to), image["name"])] = image
        if len(batch) < count:
            break
        offset += count
    return images


def upload_image(auth: str, page_id: int, page_num: int, existing: dict[tuple[int, str], dict]) -> str:
    image_path = IMAGE_DIR / f"bp802alv-p{page_num:03d}.jpg"
    if not image_path.exists():
        raise RuntimeError(f"Missing rendered image: {image_path}")
    image_name = image_path.name
    found = existing.get((page_id, image_name))
    if found:
        content = request("GET", f"/image-gallery/{found['id']}", auth)
        return content["content"]["markdown"]
    image = multipart_request(
        "/image-gallery",
        auth,
        {"type": "gallery", "uploaded_to": str(page_id), "name": image_name},
        {"image": image_path},
    )
    existing[(page_id, image_name)] = image
    return image["content"]["markdown"]


def source_page_numbers(markdown: str) -> list[int]:
    return [int(match) for match in re.findall(r"<!-- Source PDF page (\d+) -->", markdown)]


def strip_existing_page_images(markdown: str) -> str:
    return re.sub(r"\n!\[bp802alv-p\d{3}\.jpg\]\([^)]+\)\n", "\n", markdown)


def insert_images(markdown: str, image_markdown: dict[int, str]) -> str:
    markdown = strip_existing_page_images(markdown)
    for page_num, image in image_markdown.items():
        marker = f"<!-- Source PDF page {page_num} -->"
        markdown = markdown.replace(marker, f"{marker}\n\n{image}", 1)
    return markdown


def main() -> None:
    auth = token()
    payload = json.loads(PAYLOAD_PATH.read_text(encoding="utf-8"))
    book = find_book(auth)
    chapter = find_chapter(auth, int(book["id"]))
    pages = chapter_pages(auth, int(chapter["id"]))
    images = gallery_index(auth)
    updated = 0

    for chapter_payload in payload["chapters"]:
        for page_payload in chapter_payload["pages"]:
            page = pages.get(page_payload["name"])
            if not page:
                raise RuntimeError(f"BookStack page not found: {page_payload['name']}")
            page_id = int(page["id"])
            image_markdown = {
                page_num: upload_image(auth, page_id, page_num, images)
                for page_num in source_page_numbers(page_payload["markdown"])
            }
            markdown = insert_images(page_payload["markdown"], image_markdown)
            request(
                "PUT",
                f"/pages/{page_id}",
                auth,
                {
                    "book_id": int(book["id"]),
                    "chapter_id": int(chapter["id"]),
                    "name": page_payload["name"],
                    "markdown": markdown,
                },
            )
            updated += 1
            print(f"updated {page_id}: {page_payload['name']} with {len(image_markdown)} images")
    print(f"updated {updated} pages with inline page images")


if __name__ == "__main__":
    main()
