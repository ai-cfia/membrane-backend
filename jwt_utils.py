"""
Utilities for encoding, decoding, and validating JWT tokens.
"""
import logging
from pathlib import Path
from datetime import datetime
from flask import session, redirect, url_for
from jwt import decode, encode, exceptions as jwt_exceptions

class JWTError(Exception):
    """Base Class for JWT errors"""
class JWTAppIdMissingError(JWTError):
    """Raised when the app_id is missing in JWT header."""
class JWTPublicKeyNotFoundError(JWTError):
    """Raised when the public key for a given app_id is not found."""
class JWTPrivateKeyNotFoundError(JWTError):
    """Raised when the private key is not found."""
class BlacklistedTokenError(JWTError):
    """Raised when the provided token is blacklisted."""
class InvalidTokenError(JWTError):
    """Raised when the provided token is invalid."""
class InvalidClientTokenError(JWTError):
    """Raised when the provided client token is invalid."""
class InvalidEmailTokenError(JWTError):
    """Raised when the provided email token is invalid."""
class JWTExpired(JWTError):
    """Raised when the provided token is expired."""

def extract_jwt_token(jwt_token, token_blacklist):
    """
    Extract JWT token from the provided request object.
    """
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")

    # Check if token is in the blacklist.
    if jwt_token in token_blacklist:
        raise BlacklistedTokenError("This token has already been used.")

    return jwt_token

def encode_email_token(payload, server_private_key_path: Path):
    """
    Encode the payload using the private key for RS256 algorithm.
    """
    if not server_private_key_path.exists():
        raise JWTPrivateKeyNotFoundError(f'Private key not found at: {server_private_key_path}.')

    with server_private_key_path.open('r') as key_file:
        private_key = key_file.read()

    jwt_token = encode(payload, private_key, algorithm='RS256')
    return jwt_token

def decode_jwt_token(jwt_token, keys_directory: Path):
    """
    Decode the JWT token using the correct public key based on app_id.
    """
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")

     # Temporarily decode the token to fetch the app_id
    unverified_decoded_token = decode(jwt_token, options={"verify_signature": False})
    if 'app_id' not in unverified_decoded_token:
        raise JWTAppIdMissingError('No app_id in JWT payload.')

    app_id = unverified_decoded_token['app_id']

    # Look for a corresponding public key file
    public_key_path = keys_directory / f"{app_id}_public_key.pem"

    if not public_key_path.exists():
        raise JWTPublicKeyNotFoundError(f'Public key not found for app_id: {app_id}.')

    with public_key_path.open('r') as key_file:
        public_key = key_file.read()

    try:
        # Decode the token using the fetched public key
        decoded_token = decode(jwt_token, public_key, algorithms=['RS256'])
        # Retrieve the redirect URL stored in the session.
        redirect_url = decoded_token['redirect_url']
        if not redirect_url:
            raise JWTError("No redirect URL found in Token.")

        expired_time = decoded_token['exp']

        # Get current time
        current_time = datetime.utcnow()
        current_timestamp = int(current_time.timestamp())  # Convert datetime to timestamp

        # Check for token expiration
        if current_timestamp > expired_time:
            raise JWTExpired("JWT token has expired.")

        return decoded_token

    except (jwt_exceptions.InvalidTokenError, jwt_exceptions.DecodeError) as error:
        raise JWTError(str(error)) from error

def decode_email_token(jwt_token, server_public_key: Path, token_blacklist):
    """
    Decode the JWT token using the correct public key based on app_id.
    """
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")

    # Check if token is in the blacklist.
    if jwt_token in token_blacklist:
        raise BlacklistedTokenError("This token has already been used.")

    with server_public_key.open('r') as key_file:
        public_key = key_file.read()

    try:
        # Decode the token using the fetched public key
        decoded_token = decode(jwt_token, public_key, algorithms=['RS256'])
        # Retrieve the redirect URL stored in the session.
        redirect_url = decoded_token['redirect_url']
        if not redirect_url:
            raise JWTError("No redirect URL found in Token.")

        expired_time = decoded_token['exp']

        # Get current time
        current_time = datetime.utcnow()
        current_timestamp = int(current_time.timestamp())  # Convert datetime to timestamp

        # Check for token expiration
        if current_timestamp > expired_time:
            raise JWTExpired("JWT token has expired.")

        return decoded_token

    except (jwt_exceptions.InvalidTokenError, jwt_exceptions.DecodeError, jwt_exceptions.InvalidSignatureError) as error:
        raise InvalidTokenError(str(error)) from error

def login_redirect_with_client_jwt(clientapp_token, client_public_keys_directory, redirect_url_to_louis_frontend):
    """Decodes the client application token and redirects to Louis Login Frontend."""
    try:
        decode_jwt_token(clientapp_token, client_public_keys_directory)
    except Exception as error:
        # Optionally log the exception or take another appropriate action.
        raise InvalidClientTokenError("Failed to decode client application token.") from error

    redirect_url_with_token = f"{redirect_url_to_louis_frontend}?token={clientapp_token}"

    return redirect(redirect_url_with_token)

def redirect_to_client_app_using_email_token(clientapp_token, server_public_key, token_blacklist):
    """Attempts to decode the client application's email token and redirects to the appropriate endpoint."""
    try:
        clientapp_decoded_email_token = decode_email_token(clientapp_token, server_public_key, token_blacklist)
        session['state'] = 'EMAIL_SENT'
        redirect_url_with_token = f"{url_for('authenticate')}?token={clientapp_token}"
        return redirect(redirect_url_with_token)
    except BlacklistedTokenError:
        # Log the error and proceed to try without the blacklist
        logging.exception("Token is blacklisted, trying without blacklist...")
    except InvalidTokenError as error:
        # Log the error and raise as we can't proceed further
        print("Something went wrong. Type of error:", type(error))
        raise
    
    # Handle the token without using the blacklist
    try:
        clientapp_decoded_email_token = decode_email_token(clientapp_token, server_public_key, {})
        logging.debug("Redirecting to Client app for SSO restart")
        return redirect(f"{clientapp_decoded_email_token['redirect_url']}")
    except (InvalidTokenError, BlacklistedTokenError) as error:
        raise InvalidEmailTokenError("Failed to decode client application token.") from error

def verificate_token_decode_and_redirect(email_token, server_public_key, token_blacklist):
    decoded_email_token = decode_email_token(email_token, server_public_key, token_blacklist)
    token_blacklist.add(email_token)
    session['authenticated'] = True
    session['state'] = 'USER_AUTHENTICATED'
    email_token_redirect = f"{decoded_email_token['redirect_url']}?token={email_token}"
    return redirect(email_token_redirect, code=302)
