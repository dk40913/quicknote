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
    if any(path.endswith(ext) for ext in [".mp4", ".mov", ".webm"]):
        return URLType.VIDEO
    return URLType.WEBPAGE
