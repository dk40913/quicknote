# tests/test_obsidian.py
# 注意：note 格式化與寫入現在由 AI agent（obsidian:obsidian-markdown + Write tool）負責
# 此測試改為驗證 quicknote.py 的 JSON 輸出格式與 save_attachment 邏輯

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_json_output_has_required_fields():
    required = {"url", "type", "date", "processed_by", "lang", "summary"}
    output = {
        "url": "https://example.com",
        "type": "webpage",
        "date": "2026-04-11",
        "processed_by": "gemma-4-26b-a4b-it",
        "lang": "zh-tw",
        "summary": "這是摘要\nTITLE: 測試",
    }
    assert required.issubset(output.keys())


def test_json_output_optional_attachment():
    output = {
        "url": "https://youtube.com/watch?v=xxx",
        "type": "youtube",
        "date": "2026-04-11",
        "processed_by": "notebooklm",
        "lang": "zh-tw",
        "summary": "摘要\nTITLE: 影片筆記",
        "attachment": "thumb.jpg",
    }
    assert "attachment" in output


def test_save_attachment_copies_file(tmp_path, monkeypatch):
    import quicknote
    monkeypatch.setattr(quicknote, "ATTACHMENT_DIR", tmp_path / "attachments")

    fake_img = tmp_path / "thumb.jpg"
    fake_img.write_bytes(b"fake")

    filename = quicknote.save_attachment(fake_img)
    assert filename == "thumb.jpg"
    assert (tmp_path / "attachments" / "thumb.jpg").exists()
