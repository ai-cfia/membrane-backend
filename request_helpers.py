"""
Utility functions to assist with processing and validating HTTP requests.
"""
import re


class RequestError(Exception):
    """Base Class for Request-related errors."""


class EmailError(RequestError):
    """Exception raised for email-related errors."""


class TokenError(RequestError):
    """Base token error class."""


class MissingTokenError(TokenError):
    """Raised when no token is provided."""


class InvalidTokenError(TokenError):
    """Raised when the provided token is invalid."""


def is_valid_email(email, pattern):
    """Check if the provided email is valid."""

    if not re.match(pattern, email):
        raise EmailError(f"Invalid email address: {email}")
    return True


def validate_email_from_request(email, pattern):
    """Extract and validate email."""

    # Ensure that an email was provided in the request.
    if not email:
        raise EmailError("Missing email.")

    # Validate the provided email address.
    if not is_valid_email(email, pattern):
        raise EmailError("Invalid email address.")

    return email
