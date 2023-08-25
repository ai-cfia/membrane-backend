"""
Utility functions to assist with processing and validating HTTP requests.
"""
import os
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

def is_valid_email(email):
    """Check if the provided email is valid."""
    allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
    allowed_domains = '|'.join([re.escape(domain.strip()) for domain in allowed_domains.split(',')])
    pattern = r'^[a-zA-Z0-9._%+-]+@(?:' + allowed_domains + ')$'

    if not re.match(pattern, email):
        raise EmailError(f"Invalid email address: {email}")
    return True

def check_session_authentication(session):
    """Verify if the current session is authenticated."""
    return 'authenticated' in session and session['authenticated']

def extract_email_from_request(request):
    """Extract and validate email and redirect_url from request and session."""

    # Extract email from the request data.
    email = request.get_json().get('email')

    # Ensure that an email was provided in the request.
    if not email:
        raise EmailError("Missing email.")

    # Validate the provided email address.
    if not is_valid_email(email):
        raise EmailError("Invalid email address.")

    return email
