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
    return title[:40] or "unnamed"


def _extract_title(summary: str) -> str:
    first_non_empty = None
    for line in summary.splitlines():
        if line.startswith("TITLE:"):
            return line.replace("TITLE:", "").strip()
        if first_non_empty is None and line.strip():
            first_non_empty = line.strip()[:30]
    return first_non_empty or "未命名筆記"


def save_attachment(image_path: Path, slug: str = "") -> str:
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{slug}_" if slug else ""
    dest = ATTACHMENT_DIR / f"{stem}{image_path.name}"
    shutil.copy2(image_path, dest)
    return dest.name


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
        filename = save_attachment(image_path, slug=slug)
        image_embed = f"\n![[{filename}]]\n"

    body = "\n".join(l for l in summary.splitlines() if not l.startswith("TITLE:")).strip()

    safe_title = title.replace('"', '\\"')
    safe_url = url.replace('"', '\\"')
    content = f"""---
title: "{safe_title}"
source: "{safe_url}"
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
