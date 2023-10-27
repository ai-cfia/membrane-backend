import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urljoin

import jwt
from flask import Blueprint, Flask, redirect, request, url_for
from flask_login import LoginManager, UserMixin
from flask_login import current_user as membrane_current_user
from flask_login import login_required as _login_required
from flask_login import login_user, logout_user

ALGORITHM = "RS256"
DEFAULT_TOKEN_EXPIRATION = 300
DEFAULT_LANDING_URL = "/"
DEFAULT_LOGGED_OUT_URL = "/"
RESERVED_CLAIMS = set(["alg", "app_id", "exp", "redirect_url", "typ"])
DEFAULT_REQUIRE_LOGIN = True


@dataclass
class Certificate:
    """Represents a certificate for JWT."""

    app_id: str
    server_public_key: str
    client_private_key: str
    auth_url: str

    @classmethod
    def load(cls, certificate: str | dict):
        if isinstance(certificate, str):
            with open(certificate) as json_file:
                return cls(**json.load(json_file))
        return cls(**certificate)


@dataclass
class Configuration:
    """Configuration for membrane."""

    certificate: Certificate = None
    token_expiration = DEFAULT_TOKEN_EXPIRATION
    custom_claims = {}
    landing_url = DEFAULT_LANDING_URL
    logged_out_url = DEFAULT_LOGGED_OUT_URL
    require_login = DEFAULT_REQUIRE_LOGIN


class User(UserMixin):
    """User class for login."""

    def __init__(self, email):
        self.email = email
        self.id = email


# Initialize variables
blueprint = Blueprint("membrane", __name__)
_login_manager = LoginManager()
_config = Configuration()


class JWTError(Exception):
    """General exception for JWT-related errors."""


class JWTDecodingError(JWTError):
    """Exception raised when JWT decoding fails."""


class JWTExpMissingError(JWTError):
    """Exception raised when 'exp' field is missing in JWT."""


class JWTExpiredError(JWTError):
    """Exception raised when JWT has expired."""


def configure_membrane(
    app: Flask,
    certificate: str | dict | None,
    token_expiration: int | None = None,
    custom_claims: dict | None = None,
    landing_url: str | None = None,
    logged_out_url: str | None = None,
):
    """
    Configures membrane for a Flask app with various options.

    Args:
        app (Flask): The Flask application to attach membrane to.
        certificate (str | dict | None): Path to JSON file or dict with
            certificate info. Disables login if None.
        token_expiration (int | None, optional): JWT token validity in
            seconds. Defaults to DEFAULT_TOKEN_EXPIRATION if None.
        custom_claims (dict | None, optional): Extra claims for JWT.
            Defaults to empty dict.
        redirect_path (str | None, optional): URL path for post-auth
            redirect. Defaults to DEFAULT_REDIRECT_PATH.

    Returns:
        Flask: The configured Flask app.
    """
    _config.require_login = certificate is not None
    if _config.require_login:
        _login_manager.init_app(app)
        _config.certificate = Certificate.load(certificate)
        _config.token_expiration = token_expiration or DEFAULT_TOKEN_EXPIRATION
        _config.custom_claims = custom_claims or {}
        _check_custom_claims(_config.custom_claims)
        _config.landing_url = landing_url or DEFAULT_LANDING_URL
        _config.logged_out_url = logged_out_url or DEFAULT_LOGGED_OUT_URL
    return app


def _check_custom_claims(custom_claims: dict):
    """Check if custom claims are valid."""
    disallowed = set(custom_claims.keys()) & RESERVED_CLAIMS
    if disallowed:
        raise ValueError(f"Claims {disallowed} are reserved and must not be set.")


def _get_exp_date(token_expiration: int | None) -> int:
    """Get expiration date for JWT."""
    exp = token_expiration or _config.token_expiration
    return int((datetime.utcnow() + timedelta(seconds=exp)).timestamp())


def _landing_url() -> str:
    """Get the landing endpoint."""
    return urljoin(request.url_root, _config.landing_url)


def _logged_out_url() -> str:
    """Get the logged out endpoint."""
    return urljoin(request.url_root, _config.logged_out_url)


def _create_custom_token(
    redirect_url: str | None = None,
    token_expiration: int | None = None,
    custom_claims: dict | None = None,
) -> str:
    """Create a custom JWT token."""
    _check_custom_claims(custom_claims or {})
    payload = {
        "app_id": _config.certificate.app_id,
        "redirect_url": redirect_url or _landing_url(),
        "exp": _get_exp_date(token_expiration),
    }
    payload.update(custom_claims or _config.custom_claims)
    headers = {"alg": ALGORITHM, "app_id": _config.certificate.app_id, "typ": "JWT"}
    return _encode_jwt(payload, headers)


def _encode_jwt(payload: dict, headers: dict) -> str:
    """Encode JWT."""
    try:
        return jwt.encode(
            payload,
            _config.certificate.client_private_key,
            algorithm=ALGORITHM,
            headers=headers,
        )
    except jwt.InvalidTokenError as e:
        raise JWTDecodingError(f"JWT decoding failed: {e}") from e


def _verify_token(token: str) -> dict:
    """Verify JWT token."""
    try:
        decoded_token = jwt.decode(
            token, _config.certificate.server_public_key, algorithms=[ALGORITHM]
        )
        exp = decoded_token.get("exp")
        if not exp:
            raise JWTExpMissingError("Missing 'exp' field in the token.")
        current_time = datetime.utcnow().timestamp()
        if current_time > exp:
            raise JWTExpiredError("The token has expired.")
        return decoded_token
    except jwt.InvalidTokenError as e:
        raise JWTDecodingError(f"JWT decoding failed: {e}") from e


def membrane_login_required(f):
    """Decorator for login required routes."""

    @wraps(f)
    def decorated_view(*args, **kwargs):
        if _config.require_login:
            return _login_required(f)(*args, **kwargs)
        return f(*args, **kwargs)

    return decorated_view


@_login_manager.user_loader
def _load_user(user_id: str) -> User:
    """Load user for Flask-Login."""
    return User(user_id)


@_login_manager.unauthorized_handler
def _unauthorized():
    """Handle unauthorized access."""
    if (jwt_token := request.args.get("token")) is not None:
        if (decoded_token := _verify_token(jwt_token)) is not None:
            login_user(User(decoded_token["sub"]))
            return redirect(url_for(request.endpoint, _external=True))
    return _redirect_for_authentication()


def _redirect_for_authentication(redirect_url_after_auth=None):
    """Redirect for authentication."""
    jwt_token = _create_custom_token(redirect_url_after_auth or request.url)
    return redirect(f"{_config.certificate.auth_url}/authenticate?token={jwt_token}")


def _redirect_for_logout(user_id, redirect_url_after_auth=None):
    """"""
    claims = {"sub": user_id}
    jwt_token = _create_custom_token(
        redirect_url_after_auth or request.url, custom_claims=claims
    )
    return redirect(f"{_config.certificate.auth_url}/logout?token={jwt_token}")


@blueprint.route("/login")
def login():
    """Login route."""
    if membrane_current_user.is_authenticated:
        return redirect(_landing_url())
    return _redirect_for_authentication(_landing_url())


@blueprint.route("/logout")
def logout():
    """Logout route."""
    if not membrane_current_user.is_authenticated:
        return redirect(_logged_out_url())
    user_id = membrane_current_user.id
    logout_user()
    return _redirect_for_logout(user_id, _logged_out_url())
