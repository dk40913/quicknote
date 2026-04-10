# tests/test_summarizer.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from unittest.mock import MagicMock, patch

def test_summarize_with_gemma_text(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = "這是摘要\nTITLE: 測試標題"

    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("summarizer.genai") as mock_genai:
        mock_genai.Client.return_value = mock_client
        from summarizer import summarize_with_gemma
        result = summarize_with_gemma("測試文字內容")
        assert "摘要" in result
        assert "TITLE:" in result

def test_summarize_with_gemma_retries_on_rate_limit(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = "成功回應\nTITLE: 標題"

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        Exception("429 rate limit exceeded"),
        mock_response
    ]

    with patch("summarizer.genai") as mock_genai, \
         patch("summarizer.time.sleep") as mock_sleep:
        mock_genai.Client.return_value = mock_client
        from importlib import reload
        import summarizer
        reload(summarizer)
        result = summarizer.summarize_with_gemma("內容")
        assert mock_sleep.called
        assert "成功" in result
