# QuickNote 隨手筆記 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 給定任意 URL，自動偵測內容類型、擷取內容、生成摘要，存入 Obsidian `/隨手筆記/` 資料夾。

**Architecture:** 模組化 Python 專案。`router.py` 判斷 URL 類型，`handlers/` 各自處理不同來源，`summarizer.py` 統一呼叫 LLM，`obsidian.py` 寫入筆記，`quicknote.py` 是 CLI 入口。

**Tech Stack:** Python 3.11+、google-genai、notebooklm-py（CLI）、yt-dlp、ffmpeg、opencli

---

## 檔案結構

```
quicknote/
├── quicknote.py            ← CLI 入口
├── router.py               ← URL 類型偵測
├── summarizer.py           ← Gemma / NotebookLM 統一介面
├── obsidian.py             ← 寫入 Obsidian 筆記
├── config.py               ← 讀取環境變數
├── handlers/
│   ├── __init__.py
│   ├── youtube.py
│   ├── instagram.py
│   ├── webpage.py
│   └── video.py
├── tests/
│   ├── test_router.py
│   ├── test_obsidian.py
│   └── test_summarizer.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Task 1: 專案骨架

**Files:**
- Create: `quicknote/config.py`
- Create: `quicknote/handlers/__init__.py`
- Create: `quicknote/requirements.txt`
- Create: `quicknote/.env.example`
- Create: `quicknote/.gitignore`

- [ ] **Step 1: 建立所有目錄**

```bash
cd /Users/herb/Documents/Claude/Projects/quicknote
mkdir -p handlers tests
```

- [ ] **Step 2: 建立 config.py**

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
OBSIDIAN_PATH = os.environ.get("OBSIDIAN_PATH", "/Users/herb/Documents/Obsidian")
DEFAULT_LANG = os.environ.get("QUICKNOTE_LANG", "zh-tw")
DEFAULT_MODEL = os.environ.get("QUICKNOTE_MODEL", "gemma-4-26b-a4b-it")
NOTEBOOKLM_BIN = os.environ.get("NOTEBOOKLM_BIN", "notebooklm")
YTDLP_BIN = os.environ.get("YTDLP_BIN", "yt-dlp")
FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")
OPENCLI_BIN = os.environ.get("OPENCLI_BIN", "opencli")
```

- [ ] **Step 3: 建立 .env.example**

```bash
# .env.example
GOOGLE_API_KEY=your_google_api_key_here
OBSIDIAN_PATH=/Users/yourname/Documents/Obsidian
QUICKNOTE_LANG=zh-tw
QUICKNOTE_MODEL=gemma-4-26b-a4b-it
```

- [ ] **Step 4: 建立 requirements.txt**

```
google-genai>=0.8.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 5: 建立 .gitignore**

```
.env
__pycache__/
*.pyc
.pytest_cache/
/tmp_frames/
*.mp4
*.jpg
!tests/fixtures/
```

- [ ] **Step 6: 建立 handlers/__init__.py（空檔）**

```bash
touch handlers/__init__.py
```

- [ ] **Step 7: Commit**

```bash
git add .
git commit -m "feat: project skeleton and config"
```

---

## Task 2: router.py（URL 類型偵測）

**Files:**
- Create: `quicknote/router.py`
- Create: `quicknote/tests/test_router.py`

- [ ] **Step 1: 寫測試**

```python
# tests/test_router.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from router import detect, URLType

def test_youtube_full_url():
    assert detect("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == URLType.YOUTUBE

def test_youtube_short_url():
    assert detect("https://youtu.be/dQw4w9WgXcQ") == URLType.YOUTUBE

def test_instagram_reel():
    assert detect("https://www.instagram.com/reels/DVtHqKYiK6n/") == URLType.INSTAGRAM

def test_instagram_post():
    assert detect("https://www.instagram.com/p/ABC123/") == URLType.INSTAGRAM

def test_threads():
    assert detect("https://www.threads.net/@user/post/123") == URLType.INSTAGRAM

def test_facebook():
    assert detect("https://www.facebook.com/video/123") == URLType.INSTAGRAM

def test_direct_mp4():
    assert detect("https://example.com/video.mp4") == URLType.VIDEO

def test_direct_mov():
    assert detect("https://example.com/clip.mov") == URLType.VIDEO

def test_general_webpage():
    assert detect("https://techcrunch.com/article/ai-news") == URLType.WEBPAGE

def test_github():
    assert detect("https://github.com/user/repo") == URLType.WEBPAGE
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
cd /Users/herb/Documents/Claude/Projects/quicknote
python -m pytest tests/test_router.py -v
```

Expected: `ImportError: No module named 'router'`

- [ ] **Step 3: 實作 router.py**

```python
# router.py
from urllib.parse import urlparse
from enum import Enum

class URLType(Enum):
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    VIDEO = "video"
    WEBPAGE = "webpage"

def detect(url: str) -> URLType:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()

    if "youtube.com" in host or "youtu.be" in host:
        return URLType.YOUTUBE
    if "instagram.com" in host or "threads.net" in host or "facebook.com" in host:
        return URLType.INSTAGRAM
    if any(path.endswith(ext) for ext in [".mp4", ".mov", ".webm", ".avi"]):
        return URLType.VIDEO
    return URLType.WEBPAGE
```

- [ ] **Step 4: 執行測試確認通過**

```bash
python -m pytest tests/test_router.py -v
```

Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add router.py tests/test_router.py
git commit -m "feat: URL router with tests"
```

---

## Task 3: obsidian.py（寫入 Obsidian 筆記）

**Files:**
- Create: `quicknote/obsidian.py`
- Create: `quicknote/tests/test_obsidian.py`

- [ ] **Step 1: 寫測試**

```python
# tests/test_obsidian.py
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_extract_title_from_title_line():
    from obsidian import _extract_title
    summary = "這是內容\nTITLE: Claude AI 教學\n更多內容"
    assert _extract_title(summary) == "Claude AI 教學"

def test_extract_title_fallback():
    from obsidian import _extract_title
    summary = "這是第一行\n第二行"
    assert _extract_title(summary) == "這是第一行"

def test_slug_removes_special_chars():
    from obsidian import _slug
    result = _slug("Claude + Gamma 教學！")
    assert "+" not in result
    assert "！" not in result

def test_write_note_creates_file(tmp_path, monkeypatch):
    import obsidian
    monkeypatch.setattr(obsidian, "NOTE_DIR", tmp_path)
    monkeypatch.setattr(obsidian, "ATTACHMENT_DIR", tmp_path / "attachments")

    from obsidian import write_note
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

    # 建立假圖片
    fake_image = tmp_path / "thumb.jpg"
    fake_image.write_bytes(b"fake_image_data")

    from obsidian import write_note
    note_path = write_note(
        url="https://example.com",
        url_type="youtube",
        summary="摘要\nTITLE: 有圖片的筆記",
        processed_by="notebooklm",
        image_path=fake_image
    )
    content = note_path.read_text(encoding="utf-8")
    assert "![[" in content
    assert (tmp_path / "attachments" / "thumb.jpg").exists()
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
python -m pytest tests/test_obsidian.py -v
```

Expected: `ImportError: No module named 'obsidian'`

- [ ] **Step 3: 實作 obsidian.py**

```python
# obsidian.py
import re
import shutil
from datetime import date
from pathlib import Path
from config import OBSIDIAN_PATH

NOTE_DIR = Path(OBSIDIAN_PATH) / "隨手筆記"
ATTACHMENT_DIR = NOTE_DIR / "attachments"

def _slug(title: str) -> str:
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    return title[:40]

def _extract_title(summary: str) -> str:
    for line in summary.splitlines():
        if line.startswith("TITLE:"):
            return line.replace("TITLE:", "").strip()
    for line in summary.splitlines():
        if line.strip():
            return line.strip()[:30]
    return "未命名筆記"

def save_attachment(image_path: Path) -> str:
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    dest = ATTACHMENT_DIR / image_path.name
    shutil.copy2(image_path, dest)
    return image_path.name

def write_note(
    url: str,
    url_type: str,
    summary: str,
    processed_by: str,
    image_path: Path | None = None,
    lang: str = "zh-tw"
) -> Path:
    NOTE_DIR.mkdir(parents=True, exist_ok=True)

    title = _extract_title(summary)
    today = date.today().isoformat()
    slug = _slug(title)
    note_path = NOTE_DIR / f"{today}_{slug}.md"

    image_embed = ""
    if image_path and image_path.exists():
        filename = save_attachment(image_path)
        image_embed = f"\n![[{filename}]]\n"

    body_lines = [l for l in summary.splitlines() if not l.startswith("TITLE:")]
    body = "\n".join(body_lines).strip()

    content = f"""---
title: {title}
source: {url}
type: {url_type}
date: {today}
tags:
  - 隨手筆記
processed_by: {processed_by}
---

# {title}
{image_embed}
## 摘要與重點
{body}
"""
    note_path.write_text(content, encoding="utf-8")
    return note_path
```

- [ ] **Step 4: 執行測試確認通過**

```bash
python -m pytest tests/test_obsidian.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add obsidian.py tests/test_obsidian.py
git commit -m "feat: obsidian note writer with tests"
```

---

## Task 4: summarizer.py（LLM 統一介面）

**Files:**
- Create: `quicknote/summarizer.py`
- Create: `quicknote/tests/test_summarizer.py`

- [ ] **Step 1: 寫測試（使用 mock，不真的呼叫 API）**

```python
# tests/test_summarizer.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import MagicMock, patch

def test_summarize_with_gemma_text(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = "這是摘要\nTITLE: 測試標題"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("summarizer.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        from summarizer import summarize_with_gemma
        result = summarize_with_gemma("測試文字內容")
        assert "摘要" in result
        assert "TITLE:" in result

def test_summarize_with_gemma_retries_on_rate_limit(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = "成功回應\nTITLE: 標題"

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        Exception("429 rate limit exceeded"),
        mock_response
    ]

    with patch("summarizer.genai") as mock_genai, \
         patch("summarizer.time.sleep") as mock_sleep:
        mock_genai.Client.return_value = mock_client
        from importlib import reload
        import summarizer
        reload(summarizer)
        result = summarizer.summarize_with_gemma("內容")
        assert mock_sleep.called
        assert "成功" in result
```

- [ ] **Step 2: 執行測試確認失敗**

```bash
python -m pytest tests/test_summarizer.py -v
```

Expected: `ImportError: No module named 'summarizer'`

- [ ] **Step 3: 實作 summarizer.py**

```python
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
3. 3-5句摘要總結

最後單獨輸出一行：TITLE: <10字以內的標題>"""


def summarize_with_gemma(
    content: Union[str, list[Path]],
    lang: str = "zh-tw",
    model: str = DEFAULT_MODEL
) -> str:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    prompt = _build_prompt(lang)

    parts = []
    if isinstance(content, str):
        parts.append(content + "\n\n" + prompt)
    else:
        for frame_path in content:
            parts.append(genai_types.Part.from_bytes(
                data=frame_path.read_bytes(),
                mime_type="image/jpeg"
            ))
        parts.append(prompt)

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
    return ""


def summarize_with_notebooklm(url: str, lang: str = "zh-tw") -> str:
    lang_name = "繁體中文" if lang == "zh-tw" else "English"

    result = subprocess.run(
        [NOTEBOOKLM_BIN, "create", "--name", f"quicknote_{int(time.time())}"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"notebooklm create 失敗: {result.stderr.strip()}")

    notebook_id = result.stdout.strip()

    result = subprocess.run(
        [NOTEBOOKLM_BIN, "source", "add", notebook_id, url],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"notebooklm source add 失敗: {result.stderr.strip()}")

    question = f"請用{lang_name}摘要這份內容的主題、重點，以及3-5句總結。最後輸出一行：TITLE: <10字以內標題>"
    result = subprocess.run(
        [NOTEBOOKLM_BIN, "ask", notebook_id, question],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"notebooklm ask 失敗: {result.stderr.strip()}")

    return result.stdout.strip()
```

- [ ] **Step 4: 執行測試確認通過**

```bash
python -m pytest tests/test_summarizer.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add summarizer.py tests/test_summarizer.py
git commit -m "feat: summarizer with Gemma and NotebookLM"
```

---

## Task 5: handlers/youtube.py

**Files:**
- Create: `quicknote/handlers/youtube.py`

- [ ] **Step 1: 實作 handlers/youtube.py**

```python
# handlers/youtube.py
import subprocess
import tempfile
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
            capture_output=True
        )
        thumb = next(tmp_path.glob("thumb*.jpg"), None)

        # 若縮圖存在，先複製到系統暫存（TemporaryDirectory 結束後會刪除）
        saved_thumb = None
        if thumb:
            import shutil, tempfile as tf
            saved = tf.NamedTemporaryFile(suffix=".jpg", delete=False)
            shutil.copy2(thumb, saved.name)
            saved_thumb = Path(saved.name)

        summary = summarize_with_notebooklm(url, lang=lang)

        return {
            "summary": summary,
            "image_path": saved_thumb,
            "processed_by": "notebooklm"
        }
```

- [ ] **Step 2: 手動測試（用真實 YouTube URL）**

```bash
cd /Users/herb/Documents/Claude/Projects/quicknote
python3 -c "
from handlers.youtube import fetch
result = fetch('https://www.youtube.com/watch?v=dQw4w9WgXcQ', lang='zh-tw')
print(result['summary'][:200])
print('image:', result['image_path'])
"
```

Expected: 印出摘要開頭，image_path 為 .jpg 路徑或 None

- [ ] **Step 3: Commit**

```bash
git add handlers/youtube.py
git commit -m "feat: YouTube handler via NotebookLM"
```

---

## Task 6: handlers/instagram.py

**Files:**
- Create: `quicknote/handlers/instagram.py`

- [ ] **Step 1: 實作 handlers/instagram.py**

```python
# handlers/instagram.py
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from summarizer import summarize_with_gemma
from config import YTDLP_BIN, FFMPEG_BIN, OPENCLI_BIN, DEFAULT_MODEL


def _is_video_url(url: str) -> bool:
    return "/reels/" in url or "/reel/" in url


def fetch(url: str, lang: str = "zh-tw", model: str = DEFAULT_MODEL) -> dict:
    if _is_video_url(url):
        return _fetch_video(url, lang, model)
    return _fetch_post(url, lang, model)


def _fetch_video(url: str, lang: str, model: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        video_path = tmp_path / "video.mp4"

        result = subprocess.run(
            [YTDLP_BIN, "--cookies-from-browser", "chrome",
             "-o", str(video_path), url],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"下載失敗。請確認 Chrome 已登入 Instagram。\n{result.stderr[:200]}"
            )

        frames_dir = tmp_path / "frames"
        frames_dir.mkdir()
        subprocess.run(
            [FFMPEG_BIN, "-i", str(video_path), "-vf", "fps=1",
             str(frames_dir / "frame_%03d.jpg"), "-y"],
            capture_output=True
        )

        frames = sorted(frames_dir.glob("*.jpg"))
        if not frames:
            raise RuntimeError("影格抽取失敗")

        summary = summarize_with_gemma(frames, lang=lang, model=model)

        # 把第一張影格複製出來當縮圖（避免 tmp 被清掉）
        saved_thumb = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        shutil.copy2(frames[0], saved_thumb.name)

        return {
            "summary": summary,
            "image_path": Path(saved_thumb.name),
            "processed_by": model
        }


def _fetch_post(url: str, lang: str, model: str) -> dict:
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
```

- [ ] **Step 2: 手動測試（用今天測試過的 IG Reel）**

```bash
python3 -c "
from handlers.instagram import fetch
result = fetch('https://www.instagram.com/reels/DVtHqKYiK6n/', lang='zh-tw')
print(result['summary'][:200])
print('image:', result['image_path'])
"
```

Expected: 印出影片摘要，image_path 為第一個影格的路徑

- [ ] **Step 3: Commit**

```bash
git add handlers/instagram.py
git commit -m "feat: Instagram/Threads/FB handler"
```

---

## Task 7: handlers/webpage.py

**Files:**
- Create: `quicknote/handlers/webpage.py`

- [ ] **Step 1: 實作 handlers/webpage.py**

```python
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
```

- [ ] **Step 2: 手動測試（用一般公開網頁）**

```bash
python3 -c "
from handlers.webpage import fetch
result = fetch('https://github.com/google-gemini/cookbook', lang='zh-tw')
print(result['summary'][:200])
print('processed_by:', result['processed_by'])
"
```

Expected: 印出網頁摘要，processed_by 為 notebooklm 或 gemma-4-26b-a4b-it

- [ ] **Step 3: Commit**

```bash
git add handlers/webpage.py
git commit -m "feat: webpage handler with NotebookLM + OpenCLI fallback"
```

---

## Task 8: handlers/video.py

**Files:**
- Create: `quicknote/handlers/video.py`

- [ ] **Step 1: 實作 handlers/video.py**

```python
# handlers/video.py
import subprocess
import tempfile
import shutil
from pathlib import Path
from summarizer import summarize_with_gemma
from config import YTDLP_BIN, FFMPEG_BIN, DEFAULT_MODEL


def fetch(url: str, lang: str = "zh-tw", model: str = DEFAULT_MODEL) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        video_path = tmp_path / "video.mp4"

        result = subprocess.run(
            [YTDLP_BIN, "-o", str(video_path), url],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"影片下載失敗: {result.stderr[:200]}")

        frames_dir = tmp_path / "frames"
        frames_dir.mkdir()
        subprocess.run(
            [FFMPEG_BIN, "-i", str(video_path), "-vf", "fps=1",
             str(frames_dir / "frame_%03d.jpg"), "-y"],
            capture_output=True
        )

        frames = sorted(frames_dir.glob("*.jpg"))
        if not frames:
            raise RuntimeError("影格抽取失敗")

        summary = summarize_with_gemma(frames, lang=lang, model=model)

        saved_thumb = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        shutil.copy2(frames[0], saved_thumb.name)

        return {
            "summary": summary,
            "image_path": Path(saved_thumb.name),
            "processed_by": model
        }
```

- [ ] **Step 2: Commit**

```bash
git add handlers/video.py
git commit -m "feat: direct video URL handler"
```

---

## Task 9: quicknote.py（CLI 入口）

**Files:**
- Create: `quicknote/quicknote.py`

- [ ] **Step 1: 實作 quicknote.py**

```python
#!/usr/bin/env python3
# quicknote.py
import argparse
import sys
from router import detect, URLType
from obsidian import write_note
import handlers.youtube as youtube_handler
import handlers.instagram as instagram_handler
import handlers.webpage as webpage_handler
import handlers.video as video_handler
from config import DEFAULT_LANG, DEFAULT_MODEL

VERSION = "0.1.0"

HANDLER_MAP = {
    URLType.YOUTUBE: youtube_handler,
    URLType.INSTAGRAM: instagram_handler,
    URLType.VIDEO: video_handler,
    URLType.WEBPAGE: webpage_handler,
}

def main():
    parser = argparse.ArgumentParser(
        description="隨手筆記：URL → Obsidian"
    )
    parser.add_argument("url", help="要整理的網址")
    parser.add_argument("--lang", default=DEFAULT_LANG,
                        help="輸出語言（預設：zh-tw，可選：en）")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Gemma 模型（預設：gemma-4-26b-a4b-it）")
    parser.add_argument("--version", action="version", version=f"quicknote {VERSION}")
    args = parser.parse_args()

    print(f"🔍 分析 URL：{args.url}")
    url_type = detect(args.url)
    print(f"📌 類型：{url_type.value}")

    handler = HANDLER_MAP[url_type]

    try:
        result = handler.fetch(args.url, lang=args.lang, model=args.model)
    except Exception as e:
        print(f"❌ 處理失敗：{e}")
        note_path = write_note(
            url=args.url,
            url_type=url_type.value,
            summary=f"處理失敗，請手動整理。\n\n錯誤原因：{e}\nTITLE: 待處理",
            processed_by="error",
        )
        print(f"📝 已存待處理筆記：{note_path}")
        sys.exit(1)

    note_path = write_note(
        url=args.url,
        url_type=url_type.value,
        summary=result["summary"],
        processed_by=result["processed_by"],
        image_path=result.get("image_path"),
        lang=args.lang,
    )
    print(f"✅ 筆記已存入：{note_path}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 建立 .env（從 .env.example 複製）**

```bash
cp .env.example .env
# 填入你的 GOOGLE_API_KEY
# GOOGLE_API_KEY=（從 ai-agent-marketing-analyst/.env 複製）
```

- [ ] **Step 3: 端對端測試（用 IG Reel）**

```bash
python3 quicknote.py "https://www.instagram.com/reels/DVtHqKYiK6n/"
```

Expected:
```
🔍 分析 URL：https://www.instagram.com/reels/DVtHqKYiK6n/
📌 類型：instagram
✅ 筆記已存入：/Users/herb/Documents/Obsidian/隨手筆記/2026-04-10_<slug>.md
```

- [ ] **Step 4: 確認 Obsidian 筆記內容正確**

```bash
cat "/Users/herb/Documents/Obsidian/隨手筆記/"*.md | head -30
```

Expected: 看到 frontmatter（source, type, date, tags）+ 摘要 + 圖片 embed

- [ ] **Step 5: Commit**

```bash
git add quicknote.py .env.example
git commit -m "feat: CLI entry point, end-to-end pipeline complete"
```

---

## Task 10: Claude Code Skill 檔案

**Files:**
- Create: `quicknote/skill.md`（放進 repo，使用者自己複製到 `~/.claude/plugins/`）

- [ ] **Step 1: 建立 skill.md**

```markdown
---
name: quicknote
description: 給定 URL，自動擷取內容、生成摘要，存入 Obsidian 隨手筆記資料夾
---

# 隨手筆記 Skill

當使用者說「幫我整理這個網址」、「把這個存到筆記」、或直接貼上 URL 時，使用這個 skill。

## 執行步驟

1. 從使用者訊息取出 URL
2. 執行：`python3 ~/Documents/Claude/Projects/quicknote/quicknote.py <URL>`
3. 回報筆記存入位置

## 可選參數

- `--lang en`：英文摘要
- `--model gemma-4-31b-it`：使用較強的模型

## 範例

使用者：「幫我整理 https://www.youtube.com/watch?v=xxx」
執行：`python3 ~/Documents/Claude/Projects/quicknote/quicknote.py https://www.youtube.com/watch?v=xxx`
```

- [ ] **Step 2: Commit**

```bash
git add skill.md
git commit -m "feat: Claude Code skill definition"
```

---

## Task 11: README.md

**Files:**
- Create: `quicknote/README.md`

- [ ] **Step 1: 建立 README.md**

```markdown
# QuickNote 隨手筆記

給定任意 URL，自動偵測內容類型、擷取內容、生成摘要，存入 Obsidian `/隨手筆記/` 資料夾。

## 支援的 URL 類型

| 類型 | 處理方式 |
|------|---------|
| YouTube | NotebookLM 直接分析 |
| Instagram Reels | yt-dlp 下載 → ffmpeg 抽影格 → Gemma 4 分析 |
| Instagram 文字貼文 | OpenCLI 抓取 → Gemma 4 摘要 |
| Threads / Facebook | 同 Instagram |
| 一般網頁 | NotebookLM（失敗則 OpenCLI fallback）|
| 直接影片 URL | yt-dlp 下載 → ffmpeg → Gemma 4 |

## 安裝

### 1. Clone 專案
\`\`\`bash
git clone https://github.com/dk40913/quicknote
cd quicknote
\`\`\`

### 2. 安裝 Python 依賴
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. 安裝外部工具
\`\`\`bash
brew install yt-dlp ffmpeg
uv tool install opencli
uv tool install notebooklm-py
\`\`\`

### 4. 設定環境變數
\`\`\`bash
cp .env.example .env
# 編輯 .env，填入 GOOGLE_API_KEY 和 OBSIDIAN_PATH
\`\`\`

## 使用方法

\`\`\`bash
# 基本用法
python3 quicknote.py https://...

# 英文摘要
python3 quicknote.py https://... --lang en

# 指定模型
python3 quicknote.py https://... --model gemma-4-31b-it
\`\`\`

## Claude Code Skill 安裝

\`\`\`bash
mkdir -p ~/.claude/plugins/quicknote
cp skill.md ~/.claude/plugins/quicknote/
\`\`\`

然後在 Claude Code 對話中說：「幫我整理這個網址 https://...」
```

- [ ] **Step 2: 執行全部測試確認都通過**

```bash
python -m pytest tests/ -v
```

Expected: 所有測試通過

- [ ] **Step 3: 最終 commit**

```bash
git add README.md
git commit -m "docs: add README with installation guide"
```
