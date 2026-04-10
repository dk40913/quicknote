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
