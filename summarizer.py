# summarizer.py
import time
import subprocess
from pathlib import Path
from typing import Union
from config import GOOGLE_API_KEY, DEFAULT_MODEL, NOTEBOOKLM_BIN

try:
    from google import genai
    from google.genai import types as genai_types
except ImportError:
    genai = None
    genai_types = None


def _build_prompt(lang: str) -> str:
    lang_name = "繁體中文" if lang == "zh-tw" else "English" if lang == "en" else lang
    return f"""請用{lang_name}分析以下內容，回答：
1. 主題是什麼？
2. 最重要的關鍵文字或段落？
3. 完整摘要總結，依內容豐富度自行決定長度，重點不遺漏

最後單獨輸出一行：TITLE: <10字以內的標題>

重要：直接輸出分析內容，不要自我介紹或問候語。"""


def summarize_with_gemma(
    text: str = "",
    frames: list[Path] = None,
    lang: str = "zh-tw",
    model: str = DEFAULT_MODEL
) -> str:
    if genai is None:
        raise RuntimeError("google-genai 未安裝，請執行：pip install google-genai")
    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = _build_prompt(lang)

    parts = []
    if text:
        parts.append(text + "\n\n")
    if frames:
        for frame_path in frames:
            parts.append(genai_types.Part.from_bytes(
                data=frame_path.read_bytes(),
                mime_type="image/jpeg"
            ))
    parts.append(prompt)

    if not parts or parts == [prompt]:
        raise RuntimeError("沒有可分析的內容")

    for attempt in range(3):
        try:
            resp = client.models.generate_content(model=model, contents=parts)
            return resp.text
        except Exception as e:
            err = str(e)
            if ("429" in err or "quota" in err.lower() or "rate" in err.lower()) and attempt < 2:
                wait = 60 * (attempt + 1)
                print(f"  Rate limit，等待 {wait} 秒後重試（{attempt + 1}/3）...")
                time.sleep(wait)
            else:
                raise


def summarize_with_notebooklm(url: str, lang: str = "zh-tw") -> str:
    lang_name = "繁體中文" if lang == "zh-tw" else "English"

    result = subprocess.run(
        [NOTEBOOKLM_BIN, "create", "--name", f"quicknote_{int(time.time())}"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"notebooklm create 失敗: {result.stderr.strip()}")

    notebook_id = result.stdout.strip()

    try:
        result = subprocess.run(
            [NOTEBOOKLM_BIN, "source", "add", notebook_id, url],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(f"notebooklm source add 失敗: {result.stderr.strip()}")

        question = f"請用{lang_name}摘要這份內容的主題、重點，以及完整總結，重點不遺漏。最後輸出一行：TITLE: <10字以內標題>"
        result = subprocess.run(
            [NOTEBOOKLM_BIN, "ask", notebook_id, question],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(f"notebooklm ask 失敗: {result.stderr.strip()}")

        return result.stdout.strip()
    finally:
        subprocess.run(
            [NOTEBOOKLM_BIN, "delete", notebook_id],
            capture_output=True, text=True, timeout=120
        )
