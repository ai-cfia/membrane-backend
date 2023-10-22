"""
CFIA Membrane Backend Flask Application
"""
from flask import jsonify, redirect, request
from flask_login import current_user

from app_create import create_app
from emails import (
    EmailConfig,
    InvalidEmailError,
    send_email,
    validate_email,
)
from error_handlers import register_error_handlers
from jwt_utils import (
    JWTConfig,
    JWTError,
    decode_client_jwt_token,
    generate_client_redirect_url,
    generate_email_verification_token_url,
    login_redirect_with_client_jwt,
    redirect_to_client_app_using_verification_token,
)

app = create_app()

# Register custom error handlers for the Flask app
register_error_handlers(app)


@app.before_request
def log_request_info():
    """Log incoming request headers and body for debugging purposes."""
    app.logger.debug("Headers: %s", request.headers)
    app.logger.debug("Body: %s", request.get_data())


@app.route("/health", methods=["GET"])
def health():
    return app.config["MEMBRANE_HEALTH_MESSAGE"], 200


@app.route("/login_page")
def login_page():
    return redirect(app.config["MEMBRANE_FRONTEND"])


@app.route("/login", methods=["POST"])
def login():
    """"""
    # TODO: login without token
    try:
        token = request.args["token"]
        email = request.json["email"].lower()
        jwt_config: JWTConfig = app.config["JWT_CONFIG"]
        decoded_token = decode_client_jwt_token(token, jwt_config)
        email_config: EmailConfig = app.config["EMAIL_CONFIG"]
        validate_email(email, email_config.validation_pattern)
        body = generate_email_verification_token_url(
            email, decoded_token[jwt_config.redirect_url_field], jwt_config
        )
        send_email(email, body, email_config, app.logger)
        return jsonify({"message": email_config.email_send_success}), 200
    except KeyError:
        app.logger.error("KeyError: Missing 'token' or 'email' in request.")
        return jsonify({"error": "Missing 'token' or 'email' in request."}), 400
    except JWTError as jwt_error:
        app.logger.error(f"JWTError: {jwt_error}")
        return jsonify({"error": "Invalid or expired token."}), 401
    except InvalidEmailError as email_error:
        app.logger.error(f"EmailError: {email_error}")
        return jsonify({"error": "Invalid email"}), 400


@app.route("/authenticate", methods=["GET"])
def authenticate():
    """"""
    try:
        client_token = request.args["token"]
        jwt_config: JWTConfig = app.config["JWT_CONFIG"]
        decoded_token = decode_client_jwt_token(client_token, jwt_config)
        if current_user.is_authenticated:
            redirect_url = decoded_token[jwt_config.redirect_url_field]
            client_redirect_url = generate_client_redirect_url(
                current_user.id, redirect_url, jwt_config
            )
            return redirect(client_redirect_url)
        return login_redirect_with_client_jwt(
            app.config["MEMBRANE_FRONTEND"], client_token, jwt_config
        )
    except KeyError:
        return jsonify({"error": "Missing token"}), 400
    except JWTError as jwt_error:
        app.logger.error(f"JWT error: {jwt_error}")
        return jsonify({"error": "Invalid token"}), 401


@app.route("/verify_email", methods=["GET"])
def verify_email():
    """"""
    token = request.args["token"]
    jwt_config: JWTConfig = app.config["JWT_CONFIG"]
    return redirect_to_client_app_using_verification_token(token, jwt_config)
    # TODO: handle exceptions


if __name__ == "__main__":
    app.run(debug=True)
