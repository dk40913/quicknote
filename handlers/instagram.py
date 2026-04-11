# handlers/instagram.py
import re
import subprocess
import tempfile
import time
from pathlib import Path
from summarizer import summarize_with_gemma
from config import YTDLP_BIN, FFMPEG_BIN, OPENCLI_BIN, DEFUDDLE_BIN, DEFAULT_MODEL


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
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"下載失敗。請確認 Chrome 已登入 Instagram。\n{result.stderr[:200]}"
            )

        frames_dir = tmp_path / "frames"
        frames_dir.mkdir()
        subprocess.run(
            [FFMPEG_BIN, "-i", str(video_path), "-vf", "fps=1",
             "-vframes", "60",
             str(frames_dir / "frame_%03d.jpg"), "-y"],
            capture_output=True, timeout=120
        )

        frames = sorted(frames_dir.glob("*.jpg"))
        if not frames:
            raise RuntimeError("影格抽取失敗")

        summary = summarize_with_gemma(frames, lang=lang, model=model)

        return {
            "summary": summary,
            "image_path": None,
            "processed_by": model
        }


def _fetch_post(url: str, lang: str, model: str) -> dict:
    subprocess.run(
        [OPENCLI_BIN, "browser", "open", url],
        capture_output=True, text=True, timeout=120
    )
    time.sleep(3)

    # 抓完整 HTML 供 defuddle 解析
    html_result = subprocess.run(
        [OPENCLI_BIN, "browser", "eval", "document.documentElement.outerHTML"],
        capture_output=True, text=True, timeout=120
    )
    initial_html = html_result.stdout

    # 偵測分段標記，支援 "1/3"、"1 / 3"、"1\n/\n3" 等變體
    match = re.search(r'1\s*/\s*(\d+)', initial_html)
    total_parts = int(match.group(1)) if match else 1

    if total_parts > 1:
        print(f"  偵測到 {total_parts} 段回覆，滾動載入...")
        for _ in range(total_parts - 1):
            subprocess.run(
                [OPENCLI_BIN, "browser", "eval", "window.scrollBy(0, window.innerHeight)"],
                capture_output=True, text=True, timeout=120
            )
            time.sleep(2)

        html_result = subprocess.run(
            [OPENCLI_BIN, "browser", "eval", "document.documentElement.outerHTML"],
            capture_output=True, text=True, timeout=120
        )

    if not html_result.stdout.strip():
        raise RuntimeError("無法取得頁面內容，請確認 opencli daemon 正在執行且已登入")

    # 用 defuddle 清理 HTML → 乾淨 markdown
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_result.stdout)
        tmp_html = f.name

    try:
        defuddle_result = subprocess.run(
            [DEFUDDLE_BIN, "parse", tmp_html, "--md"],
            capture_output=True, text=True, timeout=120
        )
        clean_text = defuddle_result.stdout if defuddle_result.returncode == 0 and defuddle_result.stdout.strip() else html_result.stdout
    finally:
        Path(tmp_html).unlink(missing_ok=True)

    summary = summarize_with_gemma(clean_text, lang=lang, model=model)

    return {
        "summary": summary,
        "image_path": None,
        "processed_by": model
    }
