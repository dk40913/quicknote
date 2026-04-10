# handlers/youtube.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from summarizer import summarize_with_notebooklm
from config import YTDLP_BIN


def fetch(url: str, lang: str = "zh-tw", model: str = None) -> dict:
    """
    回傳: {"summary": str, "image_path": Path | None, "processed_by": str}
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # 下載縮圖
        subprocess.run(
            [YTDLP_BIN, "--write-thumbnail", "--skip-download",
             "--convert-thumbnails", "jpg",
             "-o", str(tmp_path / "thumb"), url],
            capture_output=True, timeout=120
        )
        thumb = next(tmp_path.glob("thumb*.jpg"), None)

        # 若縮圖存在，先複製到系統暫存（TemporaryDirectory 結束後會刪除）
        saved_thumb = None
        if thumb:
            saved = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            shutil.copy2(thumb, saved.name)
            saved_thumb = Path(saved.name)

        summary = summarize_with_notebooklm(url, lang=lang)

        return {
            "summary": summary,
            "image_path": saved_thumb,
            "processed_by": "notebooklm"
        }
