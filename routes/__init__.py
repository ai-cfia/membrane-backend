from flask import Blueprint, current_app, jsonify, redirect, request
from flask_login import current_user

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
from membrane.client.flask import membrane_current_user, membrane_login_required

blueprint = Blueprint("main", __name__)


@blueprint.route("/")
@membrane_login_required
def example_endpoint():
    user = membrane_current_user.id if hasattr(membrane_current_user, "id") else "world"
    return f"Hello, {user}!"


@blueprint.route("/health", methods=["GET"])
def health():
    return current_app.config["HEALTH_MESSAGE"], 200


@blueprint.route("/login_page")
def login_page():
    return redirect(current_app.config["MEMBRANE_FRONTEND"])


@blueprint.route("/login", methods=["POST"])
def login():
    """"""
    # TODO: login without token
    try:
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
    except KeyError:
        current_app.logger.error("KeyError: Missing 'token' or 'email' in request.")
        return jsonify({"error": "Missing 'token' or 'email' in request."}), 400
    except JWTError as jwt_error:
        current_app.logger.error(f"JWTError: {jwt_error}")
        return jsonify({"error": "Invalid or expired token."}), 401
    except InvalidEmailError as email_error:
        current_app.logger.error(f"EmailError: {email_error}")
        return jsonify({"error": "Invalid email"}), 400


@blueprint.route("/authenticate", methods=["GET"])
def authenticate():
    """"""
    try:
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
    except KeyError:
        return jsonify({"error": "Missing token"}), 400
    except JWTError as jwt_error:
        current_app.logger.error(f"JWT error: {jwt_error}")
        return jsonify({"error": "Invalid token"}), 401


@blueprint.route("/verify_email", methods=["GET"])
def verify_email():
    """"""
    token = request.args["token"]
    jwt_config: JWTConfig = current_app.config["JWT_CONFIG"]
    return redirect_to_client_app_using_verification_token(token, jwt_config)
    # TODO: handle exceptions
