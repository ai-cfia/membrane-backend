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
    jwt_token = generate_jwt_token({"data": "test_data"})
    try:
        decoded = decode_jwt_token(jwt_token, TEST_KEY_DIR)
        assert 'data' in decoded
        assert decoded['data'] == 'test_data'  # This check ensures the data was encoded properly
    except Exception as error:
        pytest.fail(f"Unexpected error: {error}")

def test_decode_jwt_with_nonexistent_app_id(generate_jwt_token):
    non_existent_app_id = "nonexistent"
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "app_id": non_existent_app_id
    }
    jwt_token = generate_jwt_token({"data": "test_data"}, header)
    with pytest.raises(JWTPublicKeyNotFoundError) as exc_info:
        decode_jwt_token(jwt_token, TEST_KEY_DIR)
    assert str(exc_info.value) == f'Public key not found for app_id: {non_existent_app_id}.'

def test_decode_jwt_with_invalid_token():
    invalid_jwt = "invalid.jwt.token"
    with pytest.raises(DecodeError):
        decode_jwt_token(invalid_jwt, TEST_KEY_DIR)
