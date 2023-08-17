"""
JWT Utility functions
"""
from pathlib import Path
from jwt import get_unverified_header, decode, exceptions as jwt_exceptions

def extract_jwt_token(request):
    """
    Extract JWT token from the provided request object.
    """
    return request.args.get('token')

def decode_jwt_token(jwt_token, keys_directory: Path):
    """
    Decode the JWT token using the correct public key based on app_id.
    """
    try:
        # Extract the header without decoding the signature or payload
        header = get_unverified_header(jwt_token)

        if 'app_id' not in header:
            return None, {'error': 'No app_id in JWT header.'}

        app_id = header['app_id']

        # Look for a corresponding public key file
        public_key_path = keys_directory / f"{app_id}_public_key.pem"

        if not public_key_path.exists():
            return None, {'error': f'Public key not found for app_id: {app_id}.'}

        with public_key_path.open('r') as key_file:
            public_key = key_file.read()

        # Decode the token using the fetched public key
        decoded_token = decode(jwt_token, public_key, algorithms=['RS256'])
        return decoded_token, None
        
    except (jwt_exceptions.InvalidTokenError, jwt_exceptions.DecodeError) as error:
        return None, {'error': str(error)}

def get_jwt_redirect_url(session):
    """
    Retrieve the JWT redirect URL from the provided session.
    """
    return session.get('redirect_url')
