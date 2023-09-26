from logging import getLogger
from unittest.mock import MagicMock, patch

from emails import (
    EmailSendingFailedError,
    EmailsException,
    PollingTimeoutError,
    send_email,
)


def test_send_email_success():
    logger = getLogger("testLogger")

    mock_result = {"status": "Succeeded", "id": "some_id"}

    with patch("azure.communication.email.EmailClient") as MockEmailClient:
        mock_instance = MockEmailClient.return_value
        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_result
        mock_instance.begin_send.return_value = mock_poller
        email = {
            "email_client": mock_instance,
            "sender_email": "sender_email",
            "recipient_email": "recipient_email",
            "subject": "subject",
            "body": "body",
        }

        try:
            result = send_email(**email, logger=logger)
            assert result == {"status": "Succeeded", "operation_id": "some_id"}
        except EmailsException:
            assert False, f"Expected {email} to be successfully sent but was not."


def test_send_email_fail():
    logger = getLogger("testLogger")

    mock_result = {"status": "Failed", "error": "some_error"}

    with patch("azure.communication.email.EmailClient") as MockEmailClient:
        mock_instance = MockEmailClient.return_value
        mock_poller = MagicMock()
        mock_poller.result.return_value = mock_result
        mock_instance.begin_send.return_value = mock_poller
        email = {
            "email_client": mock_instance,
            "sender_email": "sender_email",
            "recipient_email": "recipient_email",
            "subject": "subject",
            "body": "body",
        }

        try:
            send_email(**email, logger=logger)
            assert False, f"Expected {email} to fail but it didn't."
        except EmailSendingFailedError:
            assert True


def test_polling_timeout_error():
    logger = getLogger("testLogger")

    with patch("azure.communication.email.EmailClient") as MockEmailClient:
        mock_instance = MockEmailClient.return_value
        mock_poller = MagicMock()
        mock_poller.done.return_value = False
        mock_instance.begin_send.return_value = mock_poller

        email = {
            "email_client": mock_instance,
            "sender_email": "sender_email",
            "recipient_email": "recipient_email",
            "subject": "subject",
            "body": "body",
        }

        try:
            send_email(
                **email, logger=logger, poller_wait_time=1, timeout=10
            )  # Setting low timeout for quicker test
            assert (
                False
            ), f"Expected {email} to fail due to polling timeout but it didn't."
        except PollingTimeoutError:
            assert True