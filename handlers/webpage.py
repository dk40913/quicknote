# handlers/webpage.py
import subprocess
import time
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
    except Exception as e:
        print(f"  NotebookLM 失敗（{e}），切換 OpenCLI fallback...")

    # Fallback：OpenCLI 抓網頁文字
    subprocess.run(
        [OPENCLI_BIN, "browser", "open", url],
        capture_output=True, text=True, timeout=120
    )
    time.sleep(3)

    text_result = subprocess.run(
        [OPENCLI_BIN, "browser", "eval", "document.body.innerText"],
        capture_output=True, text=True, timeout=120
    )

    summary = summarize_with_gemma(text_result.stdout, lang=lang, model=model)

    return {
        "summary": summary,
        "image_path": None,
        "processed_by": model
    }
