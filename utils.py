"""
Utility functions
"""
import os
import re
from jwt import get_unverified_header, decode, exceptions as jwt_exceptions

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

def extract_jwt_token(request):
    return request.args.get('token')

def extract_email_from_request(request):
    return request.get_json().get('email')

def check_session_authentication(session):
    return 'authenticated' in session and session['authenticated']

def decode_jwt_token(jwt_token, KEYS):
    decoded_header = get_unverified_header(jwt_token)
    app_id = decoded_header.get('appId')

    if app_id not in KEYS:
        return None, {'error': 'Invalid appId or app not supported.'}

    try:
        decoded_token = decode(jwt_token, KEYS[app_id], algorithms=['RS256'])
        if 'redirect_url' not in decoded_token:
            return None, {'error': 'Token does not contain a redirect URL'}
        return decoded_token, None
    except jwt_exceptions.ExpiredSignatureError:
        return None, {'error': 'Token has expired'}
    except jwt_exceptions.InvalidTokenError as error:
        return None, {'error': f'Invalid token. Reason: {str(error)}'}

def get_jwt_redirect_url(session):
    return session.get('redirect_url')