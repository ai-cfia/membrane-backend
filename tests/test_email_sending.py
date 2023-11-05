import unittest
from logging import getLogger
from unittest.mock import MagicMock, patch

from conftest import TestConfig

from emails import (
    EmailSendingFailedError,
    EmailsException,
    PollingTimeoutError,
    send_email,
)


class TestEmailSending(TestConfig, unittest.TestCase):
    def test_send_email_success(self):
        logger = getLogger("testLogger")
        mock_result = {"status": "Succeeded", "id": "some_id"}

        with patch("azure.communication.email.EmailClient") as MockEmailClient:
            mock_instance = MockEmailClient.return_value
            mock_poller = MagicMock()
            mock_poller.result.return_value = mock_result
            mock_instance.begin_send.return_value = mock_poller
            self.email_config.email_client = mock_instance
            email = {
                "recipient_email": "recipient_email",
                "body": "body",
                "config": self.email_config,
            }

            try:
                result = send_email(**email, logger=logger)
                self.assertEqual(
                    result, {"status": "Succeeded", "operation_id": "some_id"}
                )
            except EmailsException:
                self.fail(f"Expected {email} to be successfully sent but was not.")

    def test_send_email_fail(self):
        logger = getLogger("testLogger")
        mock_result = {"status": "Failed", "error": "some_error"}

        with patch("azure.communication.email.EmailClient") as MockEmailClient:
            mock_instance = MockEmailClient.return_value
            mock_poller = MagicMock()
            mock_poller.result.return_value = mock_result
            mock_instance.begin_send.return_value = mock_poller
            self.email_config.email_client = mock_instance
            email = {
                "recipient_email": "recipient_email",
                "body": "body",
                "config": self.email_config,
            }

            with self.assertRaises(EmailSendingFailedError):
                send_email(**email, logger=logger)

    def test_polling_timeout_error(self):
        logger = getLogger("testLogger")

        with patch("azure.communication.email.EmailClient") as MockEmailClient:
            mock_instance = MockEmailClient.return_value
            mock_poller = MagicMock()
            mock_poller.done.return_value = False
            mock_instance.begin_send.return_value = mock_poller

            self.email_config.email_client = mock_instance
            email = {
                "recipient_email": "recipient_email",
                "body": "body",
                "config": self.email_config,
            }

            with self.assertRaises(PollingTimeoutError):
                send_email(**email, logger=logger)
