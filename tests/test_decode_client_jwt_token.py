"""
Tests for JWT Token Decoding Operations.
"""
import os

import pytest

from jwt_utils import JWTError, JWTPublicKeyNotFoundError, decode_client_jwt_token


def test_decode_jwt_without_app_id(generate_jwt_token, test_app_public_key_dir):
    """Test decoding of JWT without an app_id."""
    data = os.getenv("MEMBRANE_DATA")
    jwt_token = generate_jwt_token({os.getenv("MEMBRANE_DATA_FIELD"): data})
    with pytest.raises(JWTError, match="No app id in JWT payload."):
        decode_client_jwt_token(jwt_token, test_app_public_key_dir)


def test_decode_jwt_with_nonexistent_app_id(
    generate_jwt_token, payload: dict, test_app_public_key_dir
):
    """Test decoding of JWT with a non-existent app_id."""
    app_id_field = os.getenv("MEMBRANE_APP_ID_FIELD")
    payload.update({app_id_field: "nonexistent"})
    jwt_token = generate_jwt_token(payload)
    with pytest.raises(JWTPublicKeyNotFoundError):
        decode_client_jwt_token(jwt_token, test_app_public_key_dir)


def test_decode_jwt_with_invalid_token(test_app_public_key_dir):
    """Test decoding of an invalid JWT token."""
    invalid_jwt = "invalid.jwt.token"
    # For now let's use Exception, until jwt_utils is refactored in
    # https://github.com/ai-cfia/membrane-backend/issues/60
    with pytest.raises(Exception):
        decode_client_jwt_token(invalid_jwt, test_app_public_key_dir)


def test_decode_jwt_invalid_signature(
    generate_jwt_token, payload, test_app_public_key_dir
):
    """Test decoding a JWT token with a tampered signature."""
    jwt_token = generate_jwt_token(payload)
    # Tampering with the signature to make it invalid.
    jwt_token = jwt_token[:-3] + "abc"
    with pytest.raises(JWTError):
        decode_client_jwt_token(jwt_token, test_app_public_key_dir)


def test_decode_jwt_malformed_header(
    generate_jwt_token, payload, test_app_public_key_dir
):
    """Test decoding a JWT token with a malformed header."""
    jwt_token = generate_jwt_token(payload)
    # Manipulating the token to make its header malformed.
    jwt_parts = jwt_token.split(".")
    jwt_parts[0] = jwt_parts[0] + "malformed"
    jwt_token = ".".join(jwt_parts)
    # For now let's use Exception, until jwt_utils is refactored in
    # https://github.com/ai-cfia/membrane-backend/issues/60
    with pytest.raises(Exception):
        decode_client_jwt_token(jwt_token, test_app_public_key_dir)
