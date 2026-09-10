import json

import pytest

from tools.content_editor.app import (
    ContentStore,
    EditorError,
    sanitize_rich_text,
    slugify,
    validate_editor_request,
)


def make_site(tmp_path):
    (tmp_path / "content").mkdir()
    (tmp_path / "markdown" / "posts").mkdir(parents=True)
    (tmp_path / "markdown" / "personal").mkdir(parents=True)
    (tmp_path / "content" / "blog.json").write_text("[]\n", encoding="utf-8")
    (tmp_path / "content" / "personal.json").write_text("[]\n", encoding="utf-8")
    return ContentStore(tmp_path)


def test_create_and_edit_blog_entry(tmp_path):
    store = make_site(tmp_path)
    saved = store.save_entry(
        "blog",
        {
            "title": "A New Post",
            "slug": "a-new-post",
            "date": "2026-09-10",
            "tags": ["systems", "notes"],
            "summary": "Short summary.",
            "body_html": "<p>Hello <strong>world</strong>.</p>",
        },
    )
    assert saved["slug"] == "a-new-post"
    assert store.list_entries("blog")[0]["title"] == "A New Post"
    assert "<strong>world</strong>" in (tmp_path / "markdown" / "posts" / "a-new-post.md").read_text(encoding="utf-8")

    store.save_entry(
        "blog",
        {
            "original_slug": "a-new-post",
            "title": "Edited Post",
            "slug": "a-new-post",
            "tags": [],
            "draft": True,
            "body_html": "<p>Edited.</p>",
        },
    )
    data = json.loads((tmp_path / "content" / "blog.json").read_text(encoding="utf-8"))
    assert data[0]["title"] == "Edited Post"
    assert data[0]["draft"] is True
    assert "tags" not in data[0]


def test_delete_keeps_body_for_recovery(tmp_path):
    store = make_site(tmp_path)
    store.save_entry("personal", {"title": "Night Sky", "slug": "night-sky", "tags": [], "body_html": "<p>Stars.</p>"})
    body = tmp_path / "markdown" / "personal" / "night-sky.md"
    store.delete_entry("personal", "night-sky")
    assert store.list_entries("personal") == []
    assert body.exists()


def test_rejects_duplicate_and_unsafe_slugs(tmp_path):
    store = make_site(tmp_path)
    store.save_entry("blog", {"title": "One", "slug": "one", "tags": [], "body_html": ""})
    with pytest.raises(EditorError, match="already uses"):
        store.save_entry("blog", {"title": "Another", "slug": "one", "tags": [], "body_html": ""})
    with pytest.raises(EditorError, match="Slug may contain"):
        store.save_entry("blog", {"title": "Bad", "slug": "../bad", "tags": [], "body_html": ""})


def test_slugify():
    assert slugify("  Hello, Rich Text! ") == "hello-rich-text"


def test_rich_text_sanitizer_removes_active_content_and_unsafe_links():
    dirty = (
        '<p onclick="steal()">Safe <strong>text</strong></p>'
        '<script>alert(1)</script>'
        '<a href="javascript:alert(1)" style="color:red">bad</a>'
        '<a href="https://example.com" target="_blank">good</a>'
    )
    clean = sanitize_rich_text(dirty)
    assert "onclick" not in clean
    assert "script" not in clean
    assert "alert(1)" not in clean
    assert "javascript:" not in clean
    assert 'href="https://example.com"' in clean
    assert 'rel="noopener noreferrer"' in clean


def test_editor_request_rejects_cross_origin_and_non_json_posts():
    validate_editor_request(
        "127.0.0.1:8790", "http://127.0.0.1:8790", 8790, "application/json"
    )
    with pytest.raises(EditorError, match="host"):
        validate_editor_request("attacker.test:8790", None, 8790)
    with pytest.raises(EditorError, match="origin"):
        validate_editor_request(
            "127.0.0.1:8790", "https://attacker.test", 8790, "application/json"
        )
    with pytest.raises(EditorError, match="application/json"):
        validate_editor_request(
            "127.0.0.1:8790", "http://127.0.0.1:8790", 8790, "text/plain"
        )


def test_summary_html_is_stored_as_inert_markdown_text(tmp_path):
    store = make_site(tmp_path)
    store.save_entry(
        "blog",
        {
            "title": "Safe summary",
            "slug": "safe-summary",
            "tags": [],
            "summary": '<img src=x onerror="alert(1)"> **bold**',
            "body_html": "",
        },
    )
    data = json.loads((tmp_path / "content" / "blog.json").read_text(encoding="utf-8"))
    assert "<img" not in data[0]["summary"]
    assert "&lt;img" in data[0]["summary"]
    assert store.get_entry("blog", "safe-summary")["summary"].startswith("<img")
