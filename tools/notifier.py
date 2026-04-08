import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient


def send_slack(message: str) -> None:
    """Send a message to the configured Slack channel."""
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    client.chat_postMessage(
        channel=os.environ["SLACK_CHANNEL"],
        text=message
    )


def send_email(subject: str, body: str) -> None:
    """Send an email notification to the configured recipient."""
    msg = MIMEMultipart()
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"])) as server:
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        server.sendmail(
            os.environ["SMTP_USER"],
            os.environ["EMAIL_TO"],
            msg.as_string()
        )
