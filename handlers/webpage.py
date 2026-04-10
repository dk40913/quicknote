# handlers/webpage.py
import subprocess
import tempfile
import time
from pathlib import Path
from summarizer import summarize_with_notebooklm, summarize_with_gemma
from config import OPENCLI_BIN, DEFAULT_MODEL


def fetch(url: str, lang: str = "zh-tw", model: str = DEFAULT_MODEL) -> dict:
    # 先試 NotebookLM
    try:
        summary = summarize_with_notebooklm(url, lang=lang)
        return {
            "summary": summary,
            "image_path": None,
            "processed_by": "notebooklm"
        }
    except Exception:
        pass  # fallback 到 OpenCLI

    # Fallback：OpenCLI 抓網頁文字 + 截圖
    subprocess.run(
        [OPENCLI_BIN, "browser", "open", url],
        capture_output=True, text=True
    )
    time.sleep(3)

    text_result = subprocess.run(
        [OPENCLI_BIN, "browser", "eval", "document.body.innerText"],
        capture_output=True, text=True
    )

    saved_screenshot = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    subprocess.run(
        [OPENCLI_BIN, "browser", "screenshot", saved_screenshot.name],
        capture_output=True
    )

    summary = summarize_with_gemma(text_result.stdout, lang=lang, model=model)

    screenshot_path = Path(saved_screenshot.name)
    return {
        "summary": summary,
        "image_path": screenshot_path if screenshot_path.exists() else None,
        "processed_by": model
    }
