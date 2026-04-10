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
