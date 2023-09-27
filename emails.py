from dataclasses import dataclass
from logging import Logger

from azure.communication.email import EmailClient

DEFAULT_HTML_CONTENT = "<html><h1>{}</h1></html>"
DEFAULT_POLLER_WAIT_SECONDS = 10
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_VALIDATION_PATTERN = "^[a-zA-Z0-9._%+-]+@(?:gc.ca|outlook.com)$"
DEFAULT_SUCCESS_MESSAGE = "Valid email address, Email sent with JWT link"
DEFAULT_EMAIL_SUBJECT = "Please Verify You Email Address"


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
    subject: str = DEFAULT_EMAIL_SUBJECT
    validation_pattern: str = DEFAULT_VALIDATION_PATTERN
    email_send_success: str = DEFAULT_SUCCESS_MESSAGE
    html_content: str = DEFAULT_HTML_CONTENT
    poller_wait_seconds: int = DEFAULT_POLLER_WAIT_SECONDS
    timeout: int = DEFAULT_TIMEOUT_SECONDS


def send_email(recipient_email, body: str, config: EmailConfig, logger: Logger) -> dict:
    try:
        message = {
            "content": {
                "subject": config.subject,
                "plainText": body,
                "html": config.html_content.format(body),
            },
            "recipients": {"to": [{"address": recipient_email}]},
            "senderAddress": config.sender_email,
        }

        time_elapsed = 0
        poller = config.email_client.begin_send(message)
        while not poller.done():
            logger.debug(f"Email send poller status: {poller.status()}")
            poller.wait(config.poller_wait_seconds)
            time_elapsed += config.poller_wait_seconds

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
