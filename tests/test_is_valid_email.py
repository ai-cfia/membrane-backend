"""
Email Test Cases.
"""
import unittest

from conftest import TestConfig

from request_helpers import EmailError, is_valid_email


class TestEmailValidation(TestConfig, unittest.TestCase):
    def assert_invalid_email(self, invalid_email, email_validation_pattern):
        try:
            is_valid_email(invalid_email, email_validation_pattern)
            self.fail(f"Expected {invalid_email} to be invalid but was not.")
        except EmailError:
            self.assertTrue(True)

    def test_valid_email_from_allowed_domain(self):
        email = "test.user@inspection.gc.ca"
        try:
            self.assertTrue(is_valid_email(email, self.email_config.validation_pattern))
        except EmailError:
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
        invalid_chars = "!#%^&*()=[]{}|;<>?,:\"'\\"
        base_email = "test.user{}@inspection.gc.ca"

        for char in invalid_chars:
            invalid_email = base_email.format(char)
            self.assert_invalid_email(
                invalid_email, self.email_config.validation_pattern
            )

    def test_email_with_lookalike_utf8_characters(self):
        self.assert_invalid_email(
            "test.userа@inspection.gc.ca", self.email_config.validation_pattern
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
