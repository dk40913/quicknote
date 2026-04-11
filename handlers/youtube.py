# handlers/youtube.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from summarizer import summarize_with_notebooklm
from config import YTDLP_BIN


def fetch(url: str, lang: str = "zh-tw", model: str = None) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        subprocess.run(
            [YTDLP_BIN, "--write-thumbnail", "--skip-download",
             "--convert-thumbnails", "jpg",
             "-o", str(tmp_path / "thumb"), url],
            capture_output=True, timeout=120
        )
        thumb = next(tmp_path.glob("thumb*.jpg"), None)

        # 先摘要，成功後才複製縮圖，避免失敗時留下暫存檔
        summary = summarize_with_notebooklm(url, lang=lang)

        saved_thumb = None
        if thumb:
            saved = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            shutil.copy2(thumb, saved.name)
            saved_thumb = Path(saved.name)

        return {
            "summary": summary,
            "image_path": saved_thumb,
            "processed_by": "notebooklm"
        }
