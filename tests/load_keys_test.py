"""
Tests for JWT Token Decoding Operations.
"""
from pathlib import Path
import pytest
import jwt
from jwt.exceptions import DecodeError
from jwt_utils import decode_jwt_token, JWTPublicKeyNotFoundError, JWTError

# Sample public and private keys for test purposes
with open('tests/test_private_keys/test1_private_key.pem', 'rb') as f:
    PRIVATE_KEY = f.read()

with open('tests/test_public_keys/test1_public_key.pem', 'rb') as f:
    PUBLIC_KEY = f.read()

TEST_KEY_DIR = Path('tests/test_public_keys')

@pytest.fixture
def jwt_generator():
    """Fixture to generate JWT tokens for testing purposes."""

    def _generator(payload, headers=None):
        return jwt.encode(payload, PRIVATE_KEY, algorithm='RS256', headers=headers)

    return _generator

def test_decode_jwt_without_app_id(generate_jwt_token):
    """Test decoding of JWT without an app_id."""
    jwt_token = generate_jwt_token({"data": "test_data"})
    with pytest.raises(JWTError, match="No app_id in JWT payload."):
        decode_jwt_token(jwt_token, TEST_KEY_DIR, {})


def test_decode_jwt_with_nonexistent_app_id(generate_jwt_token):
    """Test decoding of JWT with a non-existent app_id."""
    non_existent_app_id = "nonexistent"
    payload = {
        "data": "test_data",
        "app_id": non_existent_app_id
    }
    jwt_token = generate_jwt_token(payload)
    with pytest.raises(JWTPublicKeyNotFoundError) as exc_info:
        decode_jwt_token(jwt_token, TEST_KEY_DIR, {})
    assert str(exc_info.value) == f'Public key not found for app_id: {non_existent_app_id}.'


def test_decode_jwt_with_invalid_token():
    """Test decoding of an invalid JWT token."""
    invalid_jwt = "invalid.jwt.token"
    with pytest.raises(DecodeError):
        decode_jwt_token(invalid_jwt, TEST_KEY_DIR, {})

def test_decode_jwt_invalid_signature(generate_jwt_token):
    """Test decoding a JWT token with a tampered signature."""
    jwt_token = generate_jwt_token({"data": "test_data"})

    # Tampering with the signature to make it invalid.
    jwt_token = jwt_token[:-3] + "abc"
    print(jwt_token)

    with pytest.raises(JWTError):
        decode_jwt_token(jwt_token, TEST_KEY_DIR, {})


def test_decode_jwt_malformed_header(generate_jwt_token):
    """Test decoding a JWT token with a malformed header."""
    jwt_token = generate_jwt_token({"data": "test_data"})
    # Manipulating the token to make its header malformed.
    jwt_parts = jwt_token.split('.')
    jwt_parts[0] = jwt_parts[0] + 'malformed'
    jwt_token = '.'.join(jwt_parts)

    with pytest.raises(DecodeError):
        decode_jwt_token(jwt_token, TEST_KEY_DIR, {})
