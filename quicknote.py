#!/usr/bin/env python3
# quicknote.py
import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path
from router import detect, URLType
import handlers.youtube as youtube_handler
import handlers.meta as meta_handler
import handlers.webpage as webpage_handler
import handlers.video as video_handler
from config import DEFAULT_LANG, DEFAULT_MODEL, OBSIDIAN_PATH

VERSION = "0.1.0"

ATTACHMENT_DIR = Path(OBSIDIAN_PATH) / "隨手筆記" / "attachments"

HANDLER_MAP = {
    URLType.YOUTUBE: youtube_handler,
    URLType.META: meta_handler,
    URLType.VIDEO: video_handler,
    URLType.WEBPAGE: webpage_handler,
}


def save_attachment(image_path: Path) -> str:
    ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)
    dest = ATTACHMENT_DIR / image_path.name
    shutil.copy2(image_path, dest)
    return image_path.name


def main():
    parser = argparse.ArgumentParser(description="隨手筆記：URL → Obsidian")
    parser.add_argument("url", help="要整理的網址")
    parser.add_argument("--lang", default=DEFAULT_LANG)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--version", action="version", version=f"quicknote {VERSION}")
    args = parser.parse_args()

    print(f"🔍 分析 URL：{args.url}")
    try:
        url_type = detect(args.url)
    except ValueError as e:
        print(f"❌ 無效的 URL：{e}", file=sys.stderr)
        sys.exit(1)
    print(f"📌 類型：{url_type.value}")

    handler = HANDLER_MAP[url_type]

    try:
        result = handler.fetch(args.url, lang=args.lang, model=args.model)
    except Exception as e:
        print(f"❌ 處理失敗：{e}", file=sys.stderr)
        sys.exit(1)

    attachment = None
    tmp_img = result.get("image_path")
    if tmp_img and Path(str(tmp_img)).exists():
        attachment = save_attachment(Path(str(tmp_img)))
        Path(str(tmp_img)).unlink(missing_ok=True)

    output = {
        "url": args.url,
        "type": url_type.value,
        "date": date.today().isoformat(),
        "processed_by": result["processed_by"],
        "lang": args.lang,
        "summary": result["summary"],
    }
    if attachment:
        output["attachment"] = attachment

    print("\n=== QUICKNOTE ===")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
