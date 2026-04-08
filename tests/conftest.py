import pytest
from unittest.mock import MagicMock, patch
import anthropic


@pytest.fixture
def mock_anthropic_client():
    """Returns a mock Anthropic client with a configurable response."""
    client = MagicMock(spec=anthropic.Anthropic)
    return client


def make_text_response(text: str):
    """Helper to build a mock Anthropic message response with text content."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"
    return response


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("LINEAR_API_KEY", "test-linear-key")
    monkeypatch.setenv("OUTLINE_API_KEY", "test-outline-key")
    monkeypatch.setenv("OUTLINE_BASE_URL", "https://outline.test")
    monkeypatch.setenv("GITHUB_TOKEN", "test-gh-token")
    monkeypatch.setenv("GITHUB_REPO", "testowner/testrepo")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test")
    monkeypatch.setenv("SLACK_CHANNEL", "#qa-test")
    monkeypatch.setenv("SMTP_HOST", "smtp.test.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "test@test.com")
    monkeypatch.setenv("SMTP_PASSWORD", "testpass")
    monkeypatch.setenv("EMAIL_TO", "team@test.com")
    monkeypatch.setenv("MAVEN_PROJECT_PATH", "/tmp/maven-test")
    monkeypatch.setenv("PLAYWRIGHT_PROJECT_PATH", "/tmp/playwright-test")
    monkeypatch.setenv("APPIUM_PROJECT_PATH", "/tmp/appium-test")
