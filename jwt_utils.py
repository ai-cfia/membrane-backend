"""
Utilities for encoding, decoding, and validating JWT tokens.
"""
import logging
from copy import copy
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from jwt import decode, encode
from jwt import exceptions as jwt_exceptions
from quart import redirect, url_for


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


@dataclass
class JWTConfig:
    client_public_keys_folder: Path
    server_public_key: Path
    server_private_key: Path
    app_id_field: str
    redirect_url_field: str
    expiration_field: str
    algorithm: str
    data_field: str
    jwt_access_token_expire_seconds: int
    jwt_expire_seconds: int
    token_blacklist: set
    token_type: str = "JWT"


def decode_client_jwt_token(jwt_token, config: JWTConfig):
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")
    try:
        # Temporarily decode the token to fetch the app_id
        unverified_decoded_token = decode(
            jwt_token, options={"verify_signature": False}
        )
        if config.app_id_field not in unverified_decoded_token:
            raise JWTAppIdMissingError("No app id in JWT payload.")

        app_id = unverified_decoded_token[config.app_id_field]

        # Look for a corresponding public key file
        public_key_path = config.client_public_keys_folder / f"{app_id}_public_key.pem"

        if not public_key_path.exists():
            raise JWTPublicKeyNotFoundError(
                f"Public key not found for app_id: {app_id} {unverified_decoded_token}."
            )

        with public_key_path.open("r") as key_file:
            public_key = key_file.read()

        # Decode the token using the fetched public key
        decoded_token = decode(jwt_token, public_key, algorithms=[config.algorithm])
        # Retrieve the redirect URL.
        redirect_url = decoded_token[config.redirect_url_field]
        if not redirect_url:
            raise JWTError("No redirect URL found in Token.")

        expired_time = decoded_token[config.expiration_field]

        # Get current time
        current_time = datetime.utcnow()
        current_timestamp = int(current_time.timestamp())

        # Check for token expiration
        if current_timestamp > expired_time:
            raise JWTExpired("JWT token has expired.")

        return decoded_token

    except jwt_exceptions.InvalidTokenError as error:
        raise JWTError(f"{error}") from error


def login_redirect_with_client_jwt(
    membrane_frontend: str, client_app_token: str, config: JWTConfig
):
    try:
        decode_client_jwt_token(client_app_token, config)
        redirect_url_with_token = f"{membrane_frontend}?token={client_app_token}"
        return redirect(redirect_url_with_token)
    except Exception as error:
        logging.error("Failed to decode client application token: %s", error)
        raise InvalidClientTokenError(
            "Failed to decode client application token."
        ) from error


def process_email_verification_token(email_token: str, config: JWTConfig):
    try:
        decoded_email_token = decode_email_verification_token(email_token, config)
        config.token_blacklist.add(email_token)
        email_token_redirect = (
            f"{decoded_email_token[config.redirect_url_field]}?token={email_token}"
        )
        return redirect(email_token_redirect, code=302)
    except JWTError as error:
        logging.error(f"Failed to verify and decode email token: {error}")
        raise


def decode_email_verification_token(jwt_token: str, config: JWTConfig):
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")
    if jwt_token in config.token_blacklist:
        raise BlacklistedTokenError("This token has been blacklisted.")
    with config.server_public_key.open("r") as key_file:
        public_key = key_file.read()
    try:
        decoded_token = decode(jwt_token, public_key, algorithms=[config.algorithm])
        if config.redirect_url_field not in decoded_token:
            raise JWTError("No redirect URL found in token.")
        expired_time = decoded_token[config.expiration_field]
        current_time = datetime.utcnow()
        if current_time.timestamp() > expired_time:
            raise JWTExpired("JWT token has expired.")
        return decoded_token
    except jwt_exceptions.InvalidTokenError as error:
        raise InvalidTokenError(str(error)) from error


def generate_email_verification_token(email: str, redirect_url: str, config: JWTConfig):
    expiration_time = datetime.utcnow() + timedelta(seconds=config.jwt_expire_seconds)
    expiration_timestamp = int(expiration_time.timestamp())
    payload = {
        "sub": email,
        config.redirect_url_field: redirect_url,
        config.expiration_field: expiration_timestamp,
    }
    email_token = encode_email_verification_token(payload, config)
    verification_url = url_for("authenticate", token=email_token, _external=True)
    return verification_url


def encode_email_verification_token(payload: dict, config: JWTConfig):
    if not config.server_private_key.exists():
        raise JWTPrivateKeyNotFoundError("Private key not found")
    with config.server_private_key.open("r") as key_file:
        private_key = key_file.read()
    try:
        jwt_token = encode(payload, private_key, algorithm=config.algorithm)
        return jwt_token
    except Exception as error:
        raise JWTError(f"Failed to encode JWT token. Error: {error}") from error


def redirect_to_client_app_using_verification_token(
    verification_token: str, config: JWTConfig
):
    try:
        return process_email_verification_token(verification_token, config)
    except BlacklistedTokenError:
        logging.exception("Token is blacklisted, trying without blacklist...")
    except InvalidTokenError:
        logging.error("Invalid token provided.")
        raise

    try:
        _config = copy(config)
        _config.token_blacklist = []
        verification_decoded_token = decode_email_verification_token(
            verification_token,
            _config,
        )
        return redirect(verification_decoded_token[config.redirect_url_field])
    except (InvalidTokenError, BlacklistedTokenError) as error:
        raise InvalidEmailTokenError(
            "Failed to decode client application token."
        ) from error
