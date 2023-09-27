"""
Tests for JWT Token Decoding Operations.
"""
from pathlib import Path

import pytest

from jwt_utils import (
    JWTConfig,
    JWTError,
    JWTPublicKeyNotFoundError,
    decode_client_jwt_token,
)


def test_decode_jwt_without_app_id(generate_jwt_token, jwt_config: JWTConfig):
    """Test decoding of JWT without an app_id."""
    payload = {jwt_config.data_field: "test_data"}
    jwt_token = generate_jwt_token(payload, jwt_config, "testapp1")
    with pytest.raises(JWTError, match="No app id in JWT payload."):
        decode_client_jwt_token(jwt_token, jwt_config)


def test_decode_jwt_with_nonexistent_app_id(
    generate_jwt_token, payload, jwt_config: JWTConfig
):
    """Test decoding of JWT with a non-existent app_id."""
    payload.update({jwt_config.app_id_field: "nonexistent"})
    jwt_token = generate_jwt_token(payload, jwt_config, "testapp1")
    with pytest.raises(JWTPublicKeyNotFoundError):
        decode_client_jwt_token(jwt_token, jwt_config)


def test_decode_jwt_with_invalid_token(jwt_config: JWTConfig):
    """Test decoding of an invalid JWT token."""
    invalid_jwt = "invalid.jwt.token"
    # For now let's use Exception, until jwt_utils is refactored in
    # https://github.com/ai-cfia/membrane-backend/issues/60
    with pytest.raises(Exception):
        decode_client_jwt_token(invalid_jwt, jwt_config)


def test_decode_jwt_invalid_signature(sample_jwt_token, jwt_config: JWTConfig):
    """Test decoding a JWT token with a tampered signature."""
    jwt_token = sample_jwt_token
    # Tampering with the signature to make it invalid.
    jwt_token = jwt_token[:-3] + "abc"
    with pytest.raises(JWTError):
        decode_client_jwt_token(jwt_token, jwt_config)


def test_decode_jwt_malformed_header(sample_jwt_token, jwt_config: JWTConfig):
    """Test decoding a JWT token with a malformed header."""
    jwt_token = sample_jwt_token
    # Manipulating the token to make its header malformed.
    jwt_parts = jwt_token.split(".")
    jwt_parts[0] = jwt_parts[0] + "malformed"
    jwt_token = ".".join(jwt_parts)
    # For now let's use Exception, until jwt_utils is refactored in
    # https://github.com/ai-cfia/membrane-backend/issues/60
    with pytest.raises(Exception):
        decode_client_jwt_token(jwt_token, jwt_config)
