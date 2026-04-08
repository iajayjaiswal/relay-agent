from unittest.mock import patch, MagicMock
from tools.outline import fetch_doc


def test_fetch_doc_returns_text_content():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "document": {
                "id": "doc-abc",
                "title": "OCR Cheque Spec",
                "text": "## Overview\nThe cheque OCR API accepts a base64 image..."
            }
        }
    }
    with patch("tools.outline.requests.post", return_value=mock_response):
        result = fetch_doc("https://outline.test/doc/abc")

    assert result["title"] == "OCR Cheque Spec"
    assert "base64" in result["text"]
