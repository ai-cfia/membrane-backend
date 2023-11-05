"""
Utilities for encoding, decoding, and validating JWT tokens.
"""
import logging
from copy import copy
from datetime import datetime, timedelta

from flask import redirect, url_for
from flask_login import login_user
from jwt import decode, encode
from jwt import exceptions as jwt_exceptions
from jwt import get_unverified_header

from config import JWTConfig
from membrane.client.flask import User


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


def decode_client_jwt_token(jwt_token, config: JWTConfig):
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")
    try:
        # Temporarily decode the token to fetch the app_id
        # TODO: anti pattern ask for forgiveness?
        header = get_unverified_header(jwt_token)
        if config.app_id_field not in header:
            raise JWTAppIdMissingError("No app id in JWT header.")

        app_id = header[config.app_id_field]
        public_key_name = f"{app_id}{config.public_key_suffix}"
        if public_key_name not in config.client_keys:
            raise JWTPublicKeyNotFoundError(
                f"Public key not found for app_id: {app_id}."
            )

        public_key = config.client_keys[public_key_name]
        decoded_token = decode(jwt_token, public_key, algorithms=[config.algorithm])
        # Retrieve the redirect URL.
        redirect_url = decoded_token[config.redirect_url_field]
        if not redirect_url:
            raise JWTError("No redirect URL found in Token.")

        expired_time = decoded_token["exp"]
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
        login_user(User(decoded_email_token["sub"]))  # TODO: decouple from flask
        return redirect(email_token_redirect, code=302)
    except JWTError as error:
        logging.error(f"Failed to verify and decode email token: {error}")
        raise


def decode_email_verification_token(jwt_token: str, config: JWTConfig):
    if not jwt_token:
        raise JWTError("No JWT token provided in query parameters.")
    if jwt_token in config.token_blacklist:
        raise BlacklistedTokenError("This token has been blacklisted.")
    try:
        decoded_token = decode(
            jwt_token, config.server_public_key, algorithms=[config.algorithm]
        )
        if config.redirect_url_field not in decoded_token:
            raise JWTError("No redirect URL found in token.")
        expired_time = decoded_token["exp"]
        current_time = datetime.utcnow()
        if current_time.timestamp() > expired_time:
            raise JWTExpired("JWT token has expired.")
        return decoded_token
    except jwt_exceptions.InvalidTokenError as error:
        raise InvalidTokenError(str(error)) from error


def generate_client_redirect_url(email: str, redirect_url: str, config: JWTConfig):
    expiration_time = datetime.utcnow() + timedelta(seconds=config.jwt_expire_seconds)
    expiration_timestamp = int(expiration_time.timestamp())
    payload = {
        "sub": email,
        "exp": expiration_timestamp,
        config.redirect_url_field: redirect_url,
    }
    token = encode_token_with_server_pk(payload, config)
    return f"{redirect_url}?token={token}"


def generate_email_verification_token_url(
    email: str, redirect_url: str, config: JWTConfig
):
    expiration_time = datetime.utcnow() + timedelta(seconds=config.jwt_expire_seconds)
    expiration_timestamp = int(expiration_time.timestamp())
    payload = {
        "sub": email,
        "exp": expiration_timestamp,
        config.redirect_url_field: redirect_url,
    }
    token = encode_token_with_server_pk(payload, config)
    return url_for("main.verify_email", token=token, _external=True)


def encode_token_with_server_pk(payload: dict, config: JWTConfig):
    if not config.server_private_key:
        raise JWTPrivateKeyNotFoundError("Private key not found")
    try:
        jwt_token = encode(
            payload, config.server_private_key, algorithm=config.algorithm
        )
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
