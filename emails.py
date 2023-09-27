from dataclasses import dataclass
from logging import Logger

from azure.communication.email import EmailClient


class EmailsException(Exception):
    """Base class for all email-related exceptions."""


class EmailSendingFailedError(EmailsException):
    """Custom Exception for email sending errors."""


class PollingTimeoutError(EmailsException):
    """Custom Exception for polling time-out during email sending."""


class UnexpectedEmailSendError(EmailsException):
    """Custom Exception for unexpected errors."""


@dataclass
class EmailConfig:
    email_client: EmailClient
    sender_email: str
    subject: str
    validation_pattern: str
    email_send_success: str
    html_content: str = "<html><h1>{}</h1></html>"
    poller_wait_time: int = 10
    timeout: int = 180


def send_email(recipient_email, body: str, config: EmailConfig, logger: Logger) -> dict:
    try:
        message = {
            "content": {
                "subject": config.subject,
                "plainText": body,
                "html": config.html_content.format(body)
                if config.html_content
                else f"<html><h1>{body}</h1></html>",
            },
            "recipients": {"to": [{"address": recipient_email}]},
            "senderAddress": config.sender_email,
        }

        time_elapsed = 0
        poller = config.email_client.begin_send(message)
        while not poller.done():
            logger.debug(f"Email send poller status: {poller.status()}")
            poller.wait(config.poller_wait_time)
            time_elapsed += config.poller_wait_time

            if time_elapsed > config.timeout:
                raise PollingTimeoutError("Polling timed out.")

        result = poller.result()
        if result["status"] == "Succeeded":
            logger.info(f"Successfully sent the email (operation id: {result['id']})")
            return {"status": "Succeeded", "operation_id": result["id"]}
        else:
            raise EmailSendingFailedError(result["error"], None)

    except EmailsException as e:
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(e)
        raise UnexpectedEmailSendError(f"An unexpected error occurred: {e}") from e
