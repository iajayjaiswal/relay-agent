import pytest
from unittest.mock import patch, MagicMock
from tools.linear import fetch_ticket, create_subtask, update_ticket_status


def test_fetch_ticket_returns_title_and_description():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "issue": {
                "id": "abc123",
                "title": "OCR Cheque QA",
                "description": "Test the cheque OCR flow end to end.",
                "state": {"name": "In Progress"},
                "assignee": {"name": "Ajay"},
                "labels": {"nodes": [{"name": "QA"}]}
            }
        }
    }
    with patch("tools.linear.requests.post", return_value=mock_response):
        result = fetch_ticket("QA-123")

    assert result["title"] == "OCR Cheque QA"
    assert result["description"] == "Test the cheque OCR flow end to end."
    assert result["state"] == "In Progress"


def test_create_subtask_returns_created_id():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"issueCreate": {"issue": {"id": "sub-456", "title": "Write test cases"}}}
    }
    with patch("tools.linear.requests.post", return_value=mock_response):
        issue_id = create_subtask(
            parent_id="abc123",
            title="Write test cases",
            description="Generate test cases for cheque OCR."
        )
    assert issue_id == "sub-456"


def test_update_ticket_status_sends_correct_mutation():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"issueUpdate": {"issue": {"id": "abc123", "state": {"name": "Done"}}}}
    }
    with patch("tools.linear.requests.post", return_value=mock_response) as mock_post:
        update_ticket_status("abc123", "Done")
        call_args = mock_post.call_args
        assert "issueUpdate" in call_args[1]["json"]["query"]
