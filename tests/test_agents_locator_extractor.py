import pytest
from unittest.mock import MagicMock
from tests.conftest import make_text_response
from agents.locator_extractor import extract_relevant_locators


def test_extract_relevant_locators_returns_filtered_map(mock_anthropic_client):
    locator_map = """LOCATOR MAP
===========
Screen: Login
  Login button:
    resource-id: com.app:id/btn_login
    class: android.widget.Button"""
    mock_anthropic_client.messages.create.return_value = make_text_response(locator_map)
    raw_locators = [
        {"resource_id": "com.app:id/btn_login", "text": "Login", "class": "android.widget.Button", "content_desc": "", "bounds": ""},
    ]
    result = extract_relevant_locators(mock_anthropic_client, raw_locators, "Test the login flow")
    assert "LOCATOR MAP" in result
    assert "com.app:id/btn_login" in result
    mock_anthropic_client.messages.create.assert_called_once()
