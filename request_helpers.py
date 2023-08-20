import os
import re

class EmailError(Exception):
    """Exception raised for email-related errors."""
    pass

class TokenError(Exception):
    """Base token error class."""
    pass

class MissingTokenError(TokenError):
    """Raised when no token is provided."""
    pass

class InvalidTokenError(TokenError):
    """Raised when the provided token is invalid."""
    pass

def is_valid_email(email):
    """
    Validates an email address.

    It checks if the email is valid and ends with one of the allowed domains.
    Allowed domains are fetched from the ALLOWED_EMAIL_DOMAINS environment variable.

    Returns:
        - True if the email is valid, False otherwise.
    """
    allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
    allowed_domains = '|'.join([re.escape(domain.strip()) for domain in allowed_domains.split(',')])
    pattern = r'^[a-zA-Z0-9._%+-]+@(?:' + allowed_domains + ')$'
    
    if not re.match(pattern, email):
        raise EmailError(f"Invalid email address: {email}")
    return True

def extract_email_from_request(request):
    return request.get_json().get('email')

def check_session_authentication(session):
    return 'authenticated' in session and session['authenticated']

def extract_jwt_token_from_args(request):
    token = request.args.get('token')  # Extract token from URL parameters

    if token is None:
        raise MissingTokenError("No token provided.")

    return token
