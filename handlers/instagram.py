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
