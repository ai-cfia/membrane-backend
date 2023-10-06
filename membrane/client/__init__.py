import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urljoin

import jwt
from flask import Blueprint, Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

ALGORITHM = "RS256"
DEFAULT_TOKEN_EXPIRATION = 3600
DEFAULT_REDIRECT_PATH = "/"
RESERVED_CLAIMS = {"alg", "app_id", "exp", "redirect_url", "typ"}


class JWTError(Exception):
    pass


class JWTDecodingError(JWTError):
    pass


class User(UserMixin):
    def __init__(self, email):
        self.email = email
        self.id = email


@dataclass
class Certificate:
    app_id: str
    server_public_key: str
    client_private_key: str
    auth_url: str


@dataclass
class Configuration:
    certificate: Certificate = None
    token_expiration = DEFAULT_TOKEN_EXPIRATION
    custom_claims = {}
    redirect_path = DEFAULT_REDIRECT_PATH


# Initialize variables
blueprint = Blueprint("auth", __name__)
_login_manager = LoginManager()
_config = Configuration()


def configure(
    app: Flask,
    certificate: str | dict,
    token_expiration: int | None = None,
    custom_claims: dict | None = None,
    redirect_path: str | None = None,
):
    _login_manager.init_app(app)
    _config.certificate = _load_certificate(certificate)
    _config.token_expiration = token_expiration or DEFAULT_TOKEN_EXPIRATION
    _config.custom_claims = custom_claims or {}
    _check_custom_claims(_config.custom_claims)
    _config.redirect_path = redirect_path or DEFAULT_REDIRECT_PATH


def _check_custom_claims(custom_claims: dict):
    disallowed = set(custom_claims.keys()) & RESERVED_CLAIMS
    if disallowed:
        raise ValueError(f"Claims {disallowed} are reserved and must not be set.")


def _load_certificate(certificate: str | dict) -> Certificate:
    if isinstance(certificate, str):
        with open(certificate) as json_file:
            return Certificate(**json.load(json_file))
    return Certificate(**certificate)


def create_custom_token(
    redirect_url: str | None = None,
    token_expiration: int | None = None,
    custom_claims: dict | None = None,
) -> str:
    _check_custom_claims(custom_claims or {})
    payload = {
        "app_id": _config.certificate.app_id,
        "redirect_url": redirect_url or _redirect_url(),
        "exp": _get_exp_date(token_expiration),
    }
    payload.update(custom_claims or _config.custom_claims)
    headers = {"alg": ALGORITHM, "app_id": _config.certificate.app_id, "typ": "JWT"}
    return _encode_jwt(payload, headers)


def _get_exp_date(token_expiration: int | None) -> int:
    exp = token_expiration or _config.token_expiration
    return int((datetime.utcnow() + timedelta(seconds=exp)).timestamp())


def _encode_jwt(payload: dict, headers: dict) -> str:
    try:
        return jwt.encode(
            payload,
            _config.certificate.client_private_key,
            algorithm=ALGORITHM,
            headers=headers,
        )
    except jwt.InvalidTokenError as e:
        raise JWTDecodingError(f"JWT decoding failed: {e}") from e


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, _config.certificate.server_public_key, algorithms=[ALGORITHM]
        )
    except jwt.InvalidTokenError as e:
        raise JWTDecodingError(f"JWT decoding failed: {e}") from e


@_login_manager.user_loader
def _load_user(user_id: str) -> User:
    return User(user_id)


@_login_manager.unauthorized_handler
def _unauthorized():
    if (jwt_token := request.args.get("token")) is not None:
        if (decoded_token := verify_token(jwt_token)) is not None:
            login_user(User(decoded_token["sub"]))
            return redirect(url_for(request.endpoint, _external=True))
    return _redirect_for_authentication()


def _redirect_for_authentication():
    jwt_token = create_custom_token()
    return redirect(f"{_config.certificate.auth_url}/authenticate?token={jwt_token}")


@blueprint.route("/login")
def login():
    if current_user:
        return redirect(_redirect_url())
    return _redirect_for_authentication()


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(_redirect_url())


def _redirect_url() -> str:
    return urljoin(request.url_root, _config.redirect_path)
