"""
Email Test Cases.
"""

from request_helpers import EmailError, is_valid_email


def assert_invalid_email(invalid_email):
    try:
        is_valid_email(invalid_email)
        assert False, f"Expected {invalid_email} to be invalid but was not."
    except EmailError:
        assert True


def test_valid_email_from_allowed_domain():
    """
    Test the is_valid_email function with a valid email from the allowed domain.
    """
    email = "test.user@inspection.gc.ca"
    try:
        assert is_valid_email(email) is True
    except EmailError:
        assert False, f"Expected {email} to be valid but was not."


def test_invalid_email_from_disallowed_domain():
    """is_valid_email with test.user@notallowed.com."""
    assert_invalid_email("test.user@notallowed.com")


def test_concatenated_emails():
    """is_valid_email with test.user1@inspection.gc.catest.user2@inspection.gc.ca"""
    assert_invalid_email("test.user1@inspection.gc.catest.user2@inspection.gc.ca")


def test_email_with_unsupported_symbols():
    """is_valid_email with test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca."""
    assert_invalid_email("test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca")


def test_email_with_lookalike_utf8_characters():
    """is_valid_email with test.userа@inspection.gc.ca."""
    assert_invalid_email("test.userа@inspection.gc.ca")


def test_misspelled_inspection_subdomain():
    """is_valid_email with user@inspektion.gc.ca."""
    assert_invalid_email("user@inspektion.gc.ca")


def test_extra_characters_in_canada_domain():
    """is_valid_email with user@canadaa.ca."""
    assert_invalid_email("user@canadaa.ca")


def test_missing_domain_extension():
    """is_valid_email with user@canada."""
    assert_invalid_email("user@canada.")


def test_missing_subdomain():
    """is_valid_email with user@canada.."""
    assert_invalid_email("user@canada.")


def test_extra_characters_in_tld():
    """is_valid_email with user@inspection.gc.caa."""
    assert_invalid_email("user@inspection.gc.caa")
