from functools import wraps

from flask import Blueprint, current_app, jsonify, redirect, request
from flask_login import current_user, logout_user

from config import EmailConfig, JWTConfig
from emails import InvalidEmailError, send_email, validate_email
from jwt_utils import (
    JWTError,
    decode_client_jwt_token,
    generate_client_redirect_url,
    generate_email_verification_token_url,
    login_redirect_with_client_jwt,
    redirect_to_client_app_using_verification_token,
)

MISSING_TOKEN_OR_EMAIL_ERROR = "Missing token or email in request."
INVALID_OR_EXPIRED_TOKEN_ERROR = "Invalid or expired token."
INVALID_EMAIL_ERROR = "Invalid email"
LOGOUT_SUCCESS_MESSAGE = "Logged out successfully"
MISSING_TOKEN_ERROR = "Missing token"
INVALID_TOKEN_ERROR = "Invalid token"
INVALID_TOKEN_ERROR_FOR_USER = "Invalid Token for User"
NOT_LOGGED_IN = "No user is logged in"

blueprint = Blueprint("main", __name__)


@blueprint.before_request
def log_request_info():
    current_app.logger.debug("Headers: %s", request.headers)
    current_app.logger.debug("Body: %s", request.get_data())


def error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            current_app.logger.error(f"KeyError: {str(e)}")
            return jsonify({"error": MISSING_TOKEN_OR_EMAIL_ERROR}), 400
        except JWTError as e:
            current_app.logger.error(f"JWTError: {str(e)}")
            return jsonify({"error": INVALID_OR_EXPIRED_TOKEN_ERROR}), 401
        except InvalidEmailError as e:
            current_app.logger.error(f"EmailError: {str(e)}")
            return jsonify({"error": INVALID_EMAIL_ERROR}), 400

    return wrapper


@blueprint.route("/health", methods=["GET"])
def health():
    """"""
    return current_app.config["HEALTH_MESSAGE"], 200


@blueprint.route("/login_page")
def login_page():
    """"""
    return redirect(current_app.config["MEMBRANE_FRONTEND"])


@blueprint.route("/login", methods=["POST"])
@error_handler
def login():
    """"""
    # TODO: login without token
    token = request.args["token"]
    email = request.json["email"].lower()
    jwt_config: JWTConfig = current_app.config["JWT_CONFIG"]
    decoded_token = decode_client_jwt_token(token, jwt_config)
    email_config: EmailConfig = current_app.config["EMAIL_CONFIG"]
    validate_email(email, email_config.validation_pattern)
    body = generate_email_verification_token_url(
        email, decoded_token[jwt_config.redirect_url_field], jwt_config
    )
    send_email(email, body, email_config, current_app.logger)
    return jsonify({"message": email_config.email_send_success}), 200


@blueprint.route("/logout")
@error_handler
def logout():
    """"""
    if not current_user.is_authenticated:
        return jsonify({"message": NOT_LOGGED_IN}), 401
    user_id = current_user.id
    token = request.args["token"]
    jwt_config: JWTConfig = current_app.config["JWT_CONFIG"]
    decoded_token = decode_client_jwt_token(token, jwt_config)
    if decoded_token.get("sub", "") != user_id:
        return jsonify({"message": INVALID_TOKEN_ERROR_FOR_USER}), 401
    logout_user()
    return jsonify({"message": LOGOUT_SUCCESS_MESSAGE}), 200


@blueprint.route("/authenticate", methods=["GET"])
@error_handler
def authenticate():
    """"""
    client_token = request.args["token"]
    jwt_config: JWTConfig = current_app.config["JWT_CONFIG"]
    decoded_token = decode_client_jwt_token(client_token, jwt_config)
    if current_user.is_authenticated:
        redirect_url = decoded_token[jwt_config.redirect_url_field]
        client_redirect_url = generate_client_redirect_url(
            current_user.id, redirect_url, jwt_config
        )
        return redirect(client_redirect_url)
    return login_redirect_with_client_jwt(
        current_app.config["MEMBRANE_FRONTEND"], client_token, jwt_config
    )


@blueprint.route("/verify_email", methods=["GET"])
@error_handler
def verify_email():
    """"""
    token = request.args["token"]
    jwt_config: JWTConfig = current_app.config["JWT_CONFIG"]
    return redirect_to_client_app_using_verification_token(token, jwt_config)
