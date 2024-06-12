"""Module with methods for working with email."""

from email.message import EmailMessage

import aiosmtplib
from .constants import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME


async def send_email(subject: str, recipient: str, body: str) -> None:
    """Send email to the given recipient.

    Args:
        subject: str - email subject.
        recipient: str - email recipient.
        body: str - email body.
    """
    message = EmailMessage()
    message['From'] = SMTP_USERNAME
    message['To'] = recipient
    message['Subject'] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=True,
    )
