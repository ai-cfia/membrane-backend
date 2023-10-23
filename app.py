"""
CFIA Membrane Backend Quart Application
"""
import traceback

from quart import jsonify, request

from app_create import create_app
from emails import EmailConfig, send_email
from error_handlers import register_error_handlers
from jwt_utils import (
    JWTConfig,
    JWTError,
    decode_client_jwt_token,
    generate_email_verification_token,
    login_redirect_with_client_jwt,
    redirect_to_client_app_using_verification_token,
)
from request_helpers import EmailError, validate_email_from_request

app = create_app()

# Register custom error handlers for the Quart app
register_error_handlers(app)


@app.before_request
async def log_request_info():
    """Log incoming request headers and body for debugging purposes."""
    app.logger.debug("Headers: %s", request.headers)
    app.logger.debug("Body: %s", await request.get_data())


@app.route("/health", methods=["GET"])
async def health():
    return app.config["MEMBRANE_HEALTH_MESSAGE"], 200


@app.route("/authenticate", methods=["GET", "POST"])
async def authenticate():
    """
    Authenticate the client request based on various possible inputs.

    This endpoint can handle three types of requests:
    1. If the request contains both a valid client JWT and an email:
        - Validates the provided email.
        - Generates a verification token and sends a verification email to the provided
        address.
    2. If the request only contains a valid client JWT without an email:
        - Redirects the user to the Membrane frontend.
    3. If client JWT decoding fails:
        - Attempts to decode using the verification token method, to validate a user
        attempting to confirm their email.

    Returns:
        JSON response or redirect, depending on the provided inputs and their
        validation.
    """
    app.logger.debug("Entering authenticate route")
    jwt_config: JWTConfig = app.config["JWT_CONFIG"]
    email_config: EmailConfig = app.config["EMAIL_CONFIG"]

    try:
        client_app_token = request.args.get("token")
        client_app_decoded_token = decode_client_jwt_token(client_app_token, jwt_config)

        if client_app_decoded_token and request.is_json:
            email = validate_email_from_request(
                (await request.get_json()).get("email"),
                email_config.validation_pattern,
            )
            body = generate_email_verification_token(
                email,
                client_app_decoded_token[jwt_config.redirect_url_field],
                jwt_config,
            )

            app.add_background_task(send_email, email, body, email_config, app.logger)
            return jsonify({"message": email_config.email_send_success}), 200
        else:
            return login_redirect_with_client_jwt(
                app.config["MEMBRANE_FRONTEND"],
                client_app_token,
                jwt_config,
            )

    except (JWTError, EmailError) as error:
        app.logger.error("Error occurred: %s\n%s", error, traceback.format_exc())
        try:
            return redirect_to_client_app_using_verification_token(
                client_app_token, jwt_config
            )
        except JWTError as inner_error:
            app.logger.error(
                "Secondary error encountered during redirect. Type of error: %s\n%s",
                type(inner_error),
                traceback.format_exc(),
            )
            # TODO: Redirect to membrane main site if token is invalid.

    return jsonify({"error": "Invalid request method"}), 405


if __name__ == "__main__":
    app.run(debug=True)
