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


def send_email(
    email_client: EmailClient,
    sender_email,
    recipient_email,
    subject,
    body,
    logger: Logger,
    html_content: str = None,
    poller_wait_time=None,
    timeout=None,
) -> dict:
    """
    Send an email using Azure Communication Services.

    Parameters:
    - connection_string (str): The connection string for Azure Communication Services.
    - sender_email (str): The sender's email address.
    - recipient_email (str): The recipient's email address.
    - subject (str): The subject of the email.
    - body (str): The plain text body content of the email.
    - logger (Logger): Logger for capturing logs.
    - html_content (str, optional): The HTML content of the email. Defaults to None.

    Returns:
    - dict: A dictionary containing the operation status and ID if successful.

    Raises:
    - EmailsException: If email sending process fails, times out or if any unexpected
    error occurs.
    """

    logger.debug(
        f"sender_email: {sender_email}, recipient_email: {recipient_email}, "
        f"subject: {subject}, body: {body}, "
        f"html_content: {html_content}, poller_wait_time: {poller_wait_time}"
    )
    try:
        message = {
            "content": {
                "subject": subject,
                "plainText": body,
                "html": html_content.format(body)
                if html_content
                else f"<html><h1>{body}</h1></html>",
            },
            "recipients": {"to": [{"address": recipient_email}]},
            "senderAddress": sender_email,
        }

        if not poller_wait_time:
            poller_wait_time = 10
        if not timeout:
            timeout = 180
        time_elapsed = 0
        poller = email_client.begin_send(message)
        while not poller.done():
            logger.debug(f"Email send poller status: {poller.status()}")
            poller.wait(poller_wait_time)
            time_elapsed += poller_wait_time

            if time_elapsed > timeout:
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
