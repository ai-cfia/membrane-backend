"""
Utility functions
"""
import os
import re

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
    return bool(re.match(pattern, email))
