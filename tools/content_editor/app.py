"""Local rich-text content editor for the personal-site repository.

The editor is intentionally separate from the generated website. It binds to
localhost, serves its own UI, and updates a collection's JSON inventory plus
the corresponding Markdown/HTML body file using atomic writes.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import secrets
import tempfile
import threading
import webbrowser
from html.parser import HTMLParser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


COLLECTIONS = {
    "blog": {
        "label": "Blog",
        "data": "content/blog.json",
        "body_dir": "markdown/posts",
    },
    "personal": {
        "label": "Personal",
        "data": "content/personal.json",
        "body_dir": "markdown/personal",
    },
}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_REQUEST_BYTES = 2 * 1024 * 1024
ALLOWED_RICH_TEXT_TAGS = {
    "a", "b", "blockquote", "br", "code", "div", "em", "h2", "h3",
    "i", "li", "ol", "p", "pre", "s", "strong", "u", "ul",
}
BLOCKED_RICH_TEXT_TAGS = {
    "applet", "audio", "embed", "form", "iframe", "math", "object",
    "script", "style", "svg", "template", "video",
}


class EditorError(ValueError):
    """A readable validation error that can be returned to the editor UI."""


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "entry"


class _RichTextSanitizer(HTMLParser):
    """Small allow-list sanitizer for the editor's generated body HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.blocked_depth = 0
        self.blocked_tag: str | None = None

    @staticmethod
    def _safe_link(value: str) -> str | None:
        value = value.strip()
        parsed = urlparse(value)
        if parsed.scheme.lower() not in {"", "http", "https", "mailto"}:
            return None
        return value

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if self.blocked_depth:
            if tag == self.blocked_tag:
                self.blocked_depth += 1
            return
        if tag in BLOCKED_RICH_TEXT_TAGS:
            self.blocked_depth = 1
            self.blocked_tag = tag
            return
        if tag not in ALLOWED_RICH_TEXT_TAGS:
            return
        safe_attrs: list[str] = []
        if tag == "a":
            values = {name.lower(): value or "" for name, value in attrs}
            href = self._safe_link(values.get("href", ""))
            if href:
                safe_attrs.append(f'href="{html.escape(href, quote=True)}"')
            title = values.get("title", "").strip()
            if title:
                safe_attrs.append(f'title="{html.escape(title, quote=True)}"')
            safe_attrs.append('rel="noopener noreferrer"')
        suffix = (" " + " ".join(safe_attrs)) if safe_attrs else ""
        self.parts.append(f"<{tag}{suffix}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if self.blocked_depth:
            if tag.lower() == self.blocked_tag:
                self.blocked_depth -= 1
                if not self.blocked_depth:
                    self.blocked_tag = None
            return
        tag = tag.lower()
        if tag in ALLOWED_RICH_TEXT_TAGS and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self.blocked_depth:
            self.parts.append(html.escape(data))


def sanitize_rich_text(value: str) -> str:
    sanitizer = _RichTextSanitizer()
    sanitizer.feed(value)
    sanitizer.close()
    return "".join(sanitizer.parts)


def validate_editor_request(
    host: str, origin: str | None, port: int, content_type: str | None = None
) -> None:
    """Block DNS-rebinding/CSRF requests before any local file operation."""
    allowed_hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
    if host.lower() not in allowed_hosts:
        raise EditorError("Request host is not allowed.")
    if origin:
        allowed_origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        if origin.rstrip("/").lower() not in allowed_origins:
            raise EditorError("Request origin is not allowed.")
    if content_type is not None:
        media_type = content_type.split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise EditorError("POST requests must use application/json.")


def _render_body(source: str) -> str:
    """Render existing Markdown for WYSIWYG editing, with a safe fallback."""
    if not source.strip():
        return ""
    try:
        import markdown

        return sanitize_rich_text(markdown.markdown(source, extensions=["extra", "sane_lists"]))
    except ImportError:
        paragraphs = [html.escape(part) for part in source.split("\n\n") if part.strip()]
        return "".join(f"<p>{part.replace(chr(10), '<br>')}</p>" for part in paragraphs)


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temporary = Path(handle.name)
    temporary.replace(path)


class ContentStore:
    """Read and update the two editable site collections."""

    def __init__(self, site_root: str | Path):
        self.site_root = Path(site_root).resolve()

    def _settings(self, collection: str) -> dict[str, str]:
        if collection not in COLLECTIONS:
            raise EditorError("Collection must be 'blog' or 'personal'.")
        return COLLECTIONS[collection]

    def _site_path(self, relative: str) -> Path:
        path = (self.site_root / relative).resolve()
        if path != self.site_root and self.site_root not in path.parents:
            raise EditorError("Content path escapes the site directory.")
        return path

    def _load_entries(self, collection: str) -> list[dict[str, Any]]:
        settings = self._settings(collection)
        path = self._site_path(settings["data"])
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise EditorError(f"Missing content file: {settings['data']}") from exc
        except json.JSONDecodeError as exc:
            raise EditorError(f"Invalid JSON in {settings['data']}: {exc}") from exc
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise EditorError(f"{settings['data']} must contain a JSON list of objects.")
        return data

    def list_entries(self, collection: str) -> list[dict[str, Any]]:
        return [
            {
                "title": item.get("title", "Untitled"),
                "slug": item.get("slug") or slugify(item.get("title", "entry")),
                "date": item.get("date", ""),
                "draft": bool(item.get("draft", False)),
            }
            for item in self._load_entries(collection)
        ]

    def get_entry(self, collection: str, slug: str) -> dict[str, Any]:
        entries = self._load_entries(collection)
        entry = next(
            (item for item in entries if (item.get("slug") or slugify(item.get("title", ""))) == slug),
            None,
        )
        if entry is None:
            raise EditorError(f"Entry '{slug}' was not found.")
        result = dict(entry)
        result["slug"] = slug
        if result.get("summary"):
            result["summary"] = html.unescape(str(result["summary"]))
        body_path = result.get("body")
        body_source = ""
        if body_path:
            path = self._site_path(str(body_path))
            if path.exists():
                body_source = path.read_text(encoding="utf-8")
        result["body_html"] = _render_body(body_source)
        return result

    def save_entry(self, collection: str, payload: dict[str, Any]) -> dict[str, Any]:
        settings = self._settings(collection)
        title = str(payload.get("title", "")).strip()
        if not title:
            raise EditorError("Title is required.")
        slug = str(payload.get("slug", "")).strip() or slugify(title)
        if not SLUG_PATTERN.fullmatch(slug):
            raise EditorError("Slug may contain lowercase letters, numbers, and single hyphens only.")

        original_slug = str(payload.get("original_slug", "")).strip()
        entries = self._load_entries(collection)
        existing_index = (
            next(
                (
                    index
                    for index, item in enumerate(entries)
                    if (item.get("slug") or slugify(item.get("title", ""))) == original_slug
                ),
                None,
            )
            if original_slug
            else None
        )
        if original_slug and existing_index is None:
            raise EditorError(f"Entry '{original_slug}' was not found.")
        for index, item in enumerate(entries):
            item_slug = item.get("slug") or slugify(item.get("title", ""))
            if item_slug == slug and index != existing_index:
                raise EditorError(f"Another entry already uses the slug '{slug}'.")

        entry = dict(entries[existing_index]) if existing_index is not None else {}
        entry.update({"title": title, "slug": slug})
        optional_text = ("summary", "date", "category")
        for field in optional_text:
            value = str(payload.get(field, "")).strip()
            if value:
                # Summaries support Markdown, but raw HTML would be preserved by
                # Python-Markdown and then marked safe by the site templates.
                # Entity-normalize it so editing is idempotent and HTML remains
                # visible text rather than executable markup.
                entry[field] = (
                    html.escape(html.unescape(value), quote=False)
                    if field == "summary"
                    else value
                )
            else:
                entry.pop(field, None)

        tags = payload.get("tags", [])
        if not isinstance(tags, list):
            raise EditorError("Tags must be a list.")
        clean_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
        if clean_tags:
            entry["tags"] = clean_tags
        else:
            entry.pop("tags", None)

        for field in ("featured", "draft"):
            if payload.get(field):
                entry[field] = True
            else:
                entry.pop(field, None)

        body_relative = f"{settings['body_dir']}/{slug}.md"
        entry["body"] = body_relative
        body_html = sanitize_rich_text(str(payload.get("body_html", "")).strip())
        _atomic_write(self._site_path(body_relative), body_html + ("\n" if body_html else ""))

        if existing_index is None:
            entries.insert(0, entry)
        else:
            entries[existing_index] = entry
        json_text = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
        _atomic_write(self._site_path(settings["data"]), json_text)
        return {"title": title, "slug": slug, "collection": collection}

    def delete_entry(self, collection: str, slug: str) -> None:
        settings = self._settings(collection)
        entries = self._load_entries(collection)
        remaining = [
            item
            for item in entries
            if (item.get("slug") or slugify(item.get("title", ""))) != slug
        ]
        if len(remaining) == len(entries):
            raise EditorError(f"Entry '{slug}' was not found.")
        # The body file is intentionally retained as a recoverable orphan.
        _atomic_write(
            self._site_path(settings["data"]),
            json.dumps(remaining, indent=2, ensure_ascii=False) + "\n",
        )


def make_handler(store: ContentStore, ui_path: Path):
    class EditorHandler(BaseHTTPRequestHandler):
        server_version = "AcadsiteContentEditor/1.0"

        def _security_headers(self, nonce: str | None = None) -> None:
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Frame-Options", "DENY")
            policy = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
            if nonce:
                policy += (
                    f"; script-src 'nonce-{nonce}'; style-src 'nonce-{nonce}'"
                    "; connect-src 'self'"
                )
            self.send_header("Content-Security-Policy", policy)

        def _validate_request(self, mutation: bool = False) -> None:
            validate_editor_request(
                self.headers.get("Host", ""),
                self.headers.get("Origin"),
                self.server.server_port,
                self.headers.get("Content-Type") if mutation else None,
            )

        def _json(self, status: HTTPStatus, payload: dict[str, Any] | list[Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self._security_headers()
            self.end_headers()
            self.wfile.write(body)

        def _error(self, status: HTTPStatus, message: str) -> None:
            self._json(status, {"error": message})

        def _payload(self) -> dict[str, Any]:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise EditorError("Content-Length must be an integer.") from exc
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise EditorError("Request body is missing or too large.")
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise EditorError("Request body must be valid JSON.") from exc
            if not isinstance(payload, dict):
                raise EditorError("Request body must be a JSON object.")
            return payload

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            try:
                self._validate_request()
                if parsed.path == "/":
                    nonce = secrets.token_urlsafe(18)
                    body = ui_path.read_text(encoding="utf-8").replace(
                        "__CSP_NONCE__", nonce
                    ).encode("utf-8")
                    self.send_response(HTTPStatus.OK)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Cache-Control", "no-store")
                    self._security_headers(nonce)
                    self.end_headers()
                    self.wfile.write(body)
                elif parsed.path == "/api/entries":
                    collection = query.get("collection", [""])[0]
                    self._json(HTTPStatus.OK, store.list_entries(collection))
                elif parsed.path == "/api/entry":
                    collection = query.get("collection", [""])[0]
                    slug = query.get("slug", [""])[0]
                    self._json(HTTPStatus.OK, store.get_entry(collection, slug))
                else:
                    self._error(HTTPStatus.NOT_FOUND, "Not found.")
            except EditorError as exc:
                self._error(HTTPStatus.BAD_REQUEST, str(exc))

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            try:
                self._validate_request(mutation=True)
                payload = self._payload()
                if parsed.path == "/api/save":
                    collection = str(payload.pop("collection", ""))
                    self._json(HTTPStatus.OK, store.save_entry(collection, payload))
                elif parsed.path == "/api/delete":
                    collection = str(payload.get("collection", ""))
                    slug = str(payload.get("slug", ""))
                    store.delete_entry(collection, slug)
                    self._json(HTTPStatus.OK, {"deleted": slug})
                else:
                    self._error(HTTPStatus.NOT_FOUND, "Not found.")
            except EditorError as exc:
                self._error(HTTPStatus.BAD_REQUEST, str(exc))

        def log_message(self, format: str, *args: Any) -> None:
            print(f"[content-editor] {format % args}")

    return EditorHandler


def main(argv: list[str] | None = None) -> int:
    default_site = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description="Edit Blog and Personal entries in a local browser.")
    parser.add_argument("--site", default=str(default_site), help="Personal-site repository path.")
    parser.add_argument("--port", type=int, default=8790, help="Local port (default: 8790).")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically.")
    args = parser.parse_args(argv)

    store = ContentStore(args.site)
    ui_path = Path(__file__).with_name("index.html")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(store, ui_path))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Content editor: {url}")
    print("Press Ctrl+C to stop. Body files are retained when entries are deleted.")
    if not args.no_open:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
