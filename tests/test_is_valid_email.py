"""
Email Test Cases.
"""

from emails import EmailConfig
from request_helpers import EmailError, is_valid_email


def assert_invalid_email(invalid_email, email_validation_pattern):
    try:
        is_valid_email(invalid_email, email_validation_pattern)
        assert False, f"Expected {invalid_email} to be invalid but was not."
    except EmailError:
        assert True


def test_valid_email_from_allowed_domain(email_config: EmailConfig):
    """
    Test the is_valid_email function with a valid email from the allowed domain.
    """
    email = "test.user@inspection.gc.ca"
    try:
        assert is_valid_email(email, email_config.validation_pattern) is True
    except EmailError:
        assert False, f"Expected {email} to be valid but was not."


def test_invalid_email_from_disallowed_domain(email_config: EmailConfig):
    """is_valid_email with test.user@notallowed.com."""
    assert_invalid_email("test.user@notallowed.com", email_config.validation_pattern)


def test_concatenated_emails(email_config: EmailConfig):
    """is_valid_email with test.user1@inspection.gc.catest.user2@inspection.gc.ca"""
    assert_invalid_email(
        "test.user1@inspection.gc.catest.user2@inspection.gc.ca",
        email_config.validation_pattern,
    )


def test_email_with_unsupported_symbols(email_config: EmailConfig):
    """is_valid_email with test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca."""
    assert_invalid_email(
        "test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca", email_config.validation_pattern
    )


def test_email_with_lookalike_utf8_characters(email_config: EmailConfig):
    """is_valid_email with test.userа@inspection.gc.ca."""
    assert_invalid_email("test.userа@inspection.gc.ca", email_config.validation_pattern)


def test_misspelled_inspection_subdomain(email_config: EmailConfig):
    """is_valid_email with user@inspektion.gc.ca."""
    assert_invalid_email("user@inspektion.gc.ca", email_config.validation_pattern)


def test_extra_characters_in_canada_domain(email_config: EmailConfig):
    """is_valid_email with user@canadaa.ca."""
    assert_invalid_email("user@canadaa.ca", email_config.validation_pattern)


def test_missing_domain_extension(email_config: EmailConfig):
    """is_valid_email with user@canada."""
    assert_invalid_email("user@canada.", email_config.validation_pattern)


def test_missing_subdomain(email_config: EmailConfig):
    """is_valid_email with user@canada.."""
    assert_invalid_email("user@canada.", email_config.validation_pattern)


def test_extra_characters_in_tld(email_config: EmailConfig):
    """is_valid_email with user@inspection.gc.caa."""
    assert_invalid_email("user@inspection.gc.caa", email_config.validation_pattern)
