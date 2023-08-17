from pathlib import Path
import pytest
import jwt
from jwt_utils import decode_jwt_token

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
    decoded, error = decode_jwt_token(jwt_token, TEST_KEY_DIR)
    assert decoded is not None  # There will always be an "app_id" of "test1"
    assert error is None
    assert decoded['data'] == 'test_data'  # This check ensures the data was encoded properly

def test_decode_jwt_with_nonexistent_app_id(generate_jwt_token):
    non_existent_app_id = "nonexistent"
    header = {
        "alg": "RS256",
        "typ": "JWT",
        "app_id": non_existent_app_id
    }
    jwt_token = generate_jwt_token({"data": "test_data"}, header)
    decoded, error = decode_jwt_token(jwt_token, TEST_KEY_DIR)
    print(error)  # This will give you more insight about where the function might be failing
    assert decoded is None
    assert error == {'error': f'Public key not found for app_id: {non_existent_app_id}.'}

def test_decode_jwt_with_invalid_token():
    invalid_jwt = "invalid.jwt.token"
    decoded, error = decode_jwt_token(invalid_jwt, TEST_KEY_DIR)
    assert decoded is None
    assert 'error' in error
