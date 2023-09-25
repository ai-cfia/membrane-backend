"""
Email Test Cases.
"""
from request_helpers import EmailError, is_valid_email


def test_valid_email_from_allowed_domain(receiver_email):
    """
    Test the is_valid_email function with a valid email from the allowed domain.
    """
    try:
        assert is_valid_email(receiver_email) is True
    except EmailError:
        assert False, f"Expected {receiver_email} to be valid but was not."


def test_invalid_emails(invalid_emails: list[str]):
    """Test the is_valid_email function with a list of invalid emails."""
    for email in invalid_emails:
        try:
            is_valid_email(email)
            assert False, f"Expected {email} to be invalid but was not."
        except EmailError:
            assert True
