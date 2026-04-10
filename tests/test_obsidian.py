# tests/test_obsidian.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from obsidian import _extract_title, _slug, write_note


def test_extract_title_from_title_line():
    summary = "這是內容\nTITLE: Claude AI 教學\n更多內容"
    assert _extract_title(summary) == "Claude AI 教學"


def test_extract_title_fallback():
    summary = "這是第一行\n第二行"
    assert _extract_title(summary) == "這是第一行"


def test_slug_removes_special_chars():
    result = _slug("Claude + Gamma 教學！")
    assert "+" not in result
    assert "！" not in result


def test_slug_returns_unnamed_for_empty():
    assert _slug("!!!") == "unnamed"


def test_write_note_creates_file(tmp_path, monkeypatch):
    import obsidian
    monkeypatch.setattr(obsidian, "NOTE_DIR", tmp_path)
    monkeypatch.setattr(obsidian, "ATTACHMENT_DIR", tmp_path / "attachments")

    note_path = write_note(
        url="https://example.com",
        url_type="webpage",
        summary="這是摘要內容\nTITLE: 測試筆記",
        processed_by="gemma-4-26b-a4b-it"
    )
    assert note_path.exists()
    content = note_path.read_text(encoding="utf-8")
    assert "https://example.com" in content
    assert "隨手筆記" in content
    assert "測試筆記" in content


def test_write_note_with_image(tmp_path, monkeypatch):
    import obsidian
    monkeypatch.setattr(obsidian, "NOTE_DIR", tmp_path)
    monkeypatch.setattr(obsidian, "ATTACHMENT_DIR", tmp_path / "attachments")

    fake_image = tmp_path / "thumb.jpg"
    fake_image.write_bytes(b"fake_image_data")

    note_path = write_note(
        url="https://example.com",
        url_type="youtube",
        summary="摘要\nTITLE: 有圖片的筆記",
        processed_by="notebooklm",
        image_path=fake_image
    )
    content = note_path.read_text(encoding="utf-8")
    assert "![[" in content
    attachments = list((tmp_path / "attachments").glob("*thumb.jpg"))
    assert len(attachments) == 1
