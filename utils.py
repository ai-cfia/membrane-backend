"""
Utility functions
"""
import re
import datetime
import jwt
from flask import current_app

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


def create_jwt(email):
    """
    Create a JWT token with the provided email.

    This function generates a JWT with the email as the payload and sets an expiration time.

    Returns:
        A JWT token as a string.
    """
    secret_key = current_app.config['SECRET_KEY']
    
    # Set the token expiration time (e.g., 30 minutes)
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    payload = {
        'email': email,
        'exp': expiration_time
    }
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
    return jwt_token
