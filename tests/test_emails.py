import unittest
from logging import getLogger
from unittest.mock import MagicMock, patch

from config import EmailConfig
from emails import (
    EmailSendingFailedError,
    EmailsException,
    PollingTimeoutError,
    send_email,
    validate_email,
)


class TestEmailConfig(EmailConfig):
    email_client = None
    sender_email = "sender"
    validation_pattern = "^[a-zA-Z0-9._+-]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$"


class TestEmails(unittest.TestCase):
    """Unit tests for email functionalities."""

    def setUp(self):
        self.email_config = TestEmailConfig()

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

    def assert_invalid_email(self, invalid_email, email_validation_pattern):
        try:
            validate_email(invalid_email, email_validation_pattern)
            self.fail(f"Expected {invalid_email} to be invalid but was not.")
        except EmailsException:
            self.assertTrue(True)

    def test_valid_email_from_allowed_domain(self):
        email = "test.user@inspection.gc.ca"
        try:
            self.assertTrue(validate_email(email, self.email_config.validation_pattern))
        except EmailsException:
            self.fail(f"Expected {email} to be valid but was not.")

    def test_invalid_email_from_disallowed_domain(self):
        self.assert_invalid_email(
            "test.user@notallowed.com", self.email_config.validation_pattern
        )

    def test_concatenated_emails(self):
        self.assert_invalid_email(
            "test.user1@inspection.gc.catest.user2@inspection.gc.ca",
            self.email_config.validation_pattern,
        )

    def test_email_with_unsupported_symbols(self):
        invalid_chars = "!#%^&*()=[]{}|;<>?,:\"'\\а"
        base_email = "test.user{}@inspection.gc.ca"

        for char in invalid_chars:
            invalid_email = base_email.format(char)
            self.assert_invalid_email(
                invalid_email, self.email_config.validation_pattern
            )

    def test_misspelled_inspection_subdomain(self):
        self.assert_invalid_email(
            "user@inspektion.gc.ca", self.email_config.validation_pattern
        )

    def test_extra_characters_in_canada_domain(self):
        self.assert_invalid_email(
            "user@canadaa.ca", self.email_config.validation_pattern
        )

    def test_missing_domain_extension(self):
        self.assert_invalid_email("user@canada.", self.email_config.validation_pattern)

    def test_missing_subdomain(self):
        self.assert_invalid_email("user@canada.", self.email_config.validation_pattern)

    def test_extra_characters_in_tld(self):
        self.assert_invalid_email(
            "user@inspection.gc.caa", self.email_config.validation_pattern
        )
