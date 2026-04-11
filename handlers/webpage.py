# handlers/webpage.py
import subprocess
from summarizer import summarize_with_notebooklm, summarize_with_gemma
from config import DEFUDDLE_BIN, DEFAULT_MODEL


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
        print(f"  NotebookLM 失敗（{e}），切換 defuddle fallback...")

    # Fallback：defuddle 直接抓 URL → 乾淨 markdown
    result = subprocess.run(
        [DEFUDDLE_BIN, "parse", url, "--md"],
        capture_output=True, text=True, timeout=120
    )
    if not result.stdout.strip():
        raise RuntimeError("defuddle 無法取得頁面內容")

    summary = summarize_with_gemma(result.stdout, lang=lang, model=model)

    return {
        "summary": summary,
        "image_path": None,
        "processed_by": model
    }
