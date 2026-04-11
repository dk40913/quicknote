# handlers/meta.py
import re
import subprocess
import tempfile
import time
from pathlib import Path
from summarizer import summarize_with_gemma
from config import YTDLP_BIN, FFMPEG_BIN, OPENCLI_BIN, DEFUDDLE_BIN, DEFAULT_MODEL


def _fetch_text(url: str) -> str:
    """用 opencli 抓頁面 HTML，經 defuddle 清理後回傳純文字"""
    subprocess.run(
        [OPENCLI_BIN, "browser", "open", url],
        capture_output=True, text=True, timeout=120
    )
    time.sleep(3)

    html_result = subprocess.run(
        [OPENCLI_BIN, "browser", "eval", "document.documentElement.outerHTML"],
        capture_output=True, text=True, timeout=120
    )
    initial_html = html_result.stdout

    # 偵測分段標記，支援 "1/3"、"1 / 3" 等變體
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
        return ""

    # defuddle 清理 HTML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_result.stdout)
        tmp_html = f.name

    try:
        defuddle_result = subprocess.run(
            [DEFUDDLE_BIN, "parse", tmp_html, "--md"],
            capture_output=True, text=True, timeout=120
        )
        return defuddle_result.stdout if defuddle_result.returncode == 0 and defuddle_result.stdout.strip() else html_result.stdout
    finally:
        Path(tmp_html).unlink(missing_ok=True)


def _fetch_frames(url: str, tmp_path: Path) -> list[Path]:
    """嘗試用 yt-dlp 下載影片並抽影格，失敗則回傳空 list"""
    video_path = tmp_path / "video.mp4"
    result = subprocess.run(
        [YTDLP_BIN, "--cookies-from-browser", "chrome", "-o", str(video_path), url],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0 or not video_path.exists():
        return []

    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    subprocess.run(
        [FFMPEG_BIN, "-i", str(video_path), "-vf", "fps=1",
         "-vframes", "60",
         str(frames_dir / "frame_%03d.jpg"), "-y"],
        capture_output=True, timeout=120
    )
    return sorted(frames_dir.glob("*.jpg"))


def fetch(url: str, lang: str = "zh-tw", model: str = DEFAULT_MODEL) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        print("  抓取頁面文字...")
        text = _fetch_text(url)

        print("  嘗試下載影片...")
        frames = _fetch_frames(url, tmp_path)

        if frames:
            print(f"  取得 {len(frames)} 張影格")
        else:
            print("  無影片內容")

        if not text and not frames:
            raise RuntimeError("無法取得頁面內容，請確認 opencli daemon 正在執行且已登入")

        summary = summarize_with_gemma(text=text, frames=frames or None, lang=lang, model=model)

        return {
            "summary": summary,
            "image_path": None,
            "processed_by": model
        }
