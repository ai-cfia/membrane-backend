"""
Utility functions
"""
import re

def is_valid_email(email):
    """
    Validates an email address.

    It checks if the email is valid and ends with one of the allowed domains 
    (gc.ca, canada.ca, or inspection.gc.ca).

    Returns:
        - True if the email is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$'
    return bool(re.match(pattern, email))
