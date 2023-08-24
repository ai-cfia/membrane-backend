"""
Utilities for encoding, decoding, and validating JWT tokens.
"""
from pathlib import Path
from datetime import datetime
from jwt import decode, encode, exceptions as jwt_exceptions

class JWTError(Exception):
    """Base Class for JWT errors"""
class JWTAppIdMissingError(JWTError):
    """Raised when the app_id is missing in JWT header."""
class JWTPublicKeyNotFoundError(JWTError):
    """Raised when the public key for a given app_id is not found."""
class JWTPrivateKeyNotFoundError(JWTError):
    """Raised when the private key is not found."""

def extract_jwt_token(request, session):
    """
    Extract JWT token from the provided request object.
    """
    jwt_token = request.args.get('token')
    redirect_url = session.get('redirect_url')

    if not jwt_token and not redirect_url:
        raise JWTError("No JWT token provided in headers and no redirect URL in session.")

    return jwt_token

def encode_jwt_token(payload, private_key_path: Path):
    """
    Encode the payload using the private key for RS256 algorithm.
    """
    if not private_key_path.exists():
        raise JWTPrivateKeyNotFoundError(f'Private key not found at: {private_key_path}.')

    with private_key_path.open('r') as key_file:
        private_key = key_file.read()

    jwt_token = encode(payload, private_key, algorithm='RS256')
    return jwt_token

def decode_jwt_token(jwt_token, keys_directory: Path):
    """
    Decode the JWT token using the correct public key based on app_id.
    """
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
            raise JWTError("No redirect URL found in session.")
        
        expired_time = decoded_token['exp']

        # Get current time
        current_time = datetime.utcnow()
        current_timestamp = int(current_time.timestamp())  # Convert datetime to timestamp
        
        # Check for token expiration
        if current_timestamp > expired_time:
            raise JWTError("JWT token has expired.")
        
        return decoded_token

    except (jwt_exceptions.InvalidTokenError, jwt_exceptions.DecodeError) as error:
        raise JWTError(str(error)) from error
