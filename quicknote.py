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
