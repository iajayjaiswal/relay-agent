from unittest.mock import patch, MagicMock
from tools.notifier import send_slack, send_email


def test_send_slack_calls_web_client_with_message():
    with patch("tools.notifier.WebClient") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        send_slack("STLC complete. 45/48 tests passed.")
        mock_client.chat_postMessage.assert_called_once()
        call_kwargs = mock_client.chat_postMessage.call_args[1]
        assert "STLC complete" in call_kwargs["text"]


def test_send_email_calls_smtp_sendmail():
    with patch("tools.notifier.smtplib.SMTP") as mock_smtp_class:
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        send_email(subject="STLC Report", body="45/48 tests passed.")
        mock_smtp.sendmail.assert_called_once()
