# handlers/video.py
import subprocess
import tempfile
from pathlib import Path
from summarizer import summarize_with_gemma
from config import YTDLP_BIN, FFMPEG_BIN, DEFAULT_MODEL


def fetch(url: str, lang: str = "zh-tw", model: str = DEFAULT_MODEL) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        video_path = tmp_path / "video.mp4"

        result = subprocess.run(
            [YTDLP_BIN, "-o", str(video_path), url],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            raise RuntimeError(f"影片下載失敗: {result.stderr[:200]}")

        frames_dir = tmp_path / "frames"
        frames_dir.mkdir()
        subprocess.run(
            [FFMPEG_BIN, "-i", str(video_path), "-vf", "fps=1",
             "-vframes", "60",
             str(frames_dir / "frame_%03d.jpg"), "-y"],
            capture_output=True, timeout=60
        )

        frames = sorted(frames_dir.glob("*.jpg"))
        if not frames:
            raise RuntimeError("影格抽取失敗")

        summary = summarize_with_gemma(frames=frames, lang=lang, model=model)

        return {
            "summary": summary,
            "image_path": None,
            "processed_by": model
        }
