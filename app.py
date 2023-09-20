"""
CFIA Louis Backend Quart Application
"""
import logging
import os
import traceback
import uuid
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from quart import Quart, jsonify, request
from quart_cors import cors
from quart_jwt_extended import JWTManager
from quart_session import Session

from emails import send_email
from environment_validation import validate_environment_settings
from error_handlers import register_error_handlers
from jwt_utils import (
    JWTError,
    decode_client_jwt_token,
    generate_email_verification_token,
    login_redirect_with_client_jwt,
    redirect_to_client_app_using_verification_token,
)
from request_helpers import EmailError, validate_email_from_request

# Load environment variables
load_dotenv()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS_LIST = ALLOWED_ORIGINS.split(",")
# Configuration paths and URLs retrieved from environment variables # TODO: Set default values
CLIENT_PUBLIC_KEYS_DIRECTORY = Path(
    os.getenv("CLIENT_PUBLIC_KEYS_DIRECTORY", "keys/public_keys")
)
SERVER_PRIVATE_KEY = Path(os.getenv("SERVER_PRIVATE_KEY", ""))
SERVER_PUBLIC_KEY = Path(os.getenv("SERVER_PUBLIC_KEY", ""))
REDIRECT_URL_TO_LOUIS_FRONTEND = os.getenv("REDIRECT_URL_TO_LOUIS_FRONTEND", "")
MEMBRANE_BACKEND_COMM_CONNECTION_STRING = os.getenv(
    "MEMBRANE_BACKEND_COMM_CONNECTION_STRING"
)
MEMBRANE_BACKEND_SENDER_EMAIL = os.getenv("MEMBRANE_BACKEND_SENDER_EMAIL")

# Validate the environment settings
validate_environment_settings(
    CLIENT_PUBLIC_KEYS_DIRECTORY,
    SERVER_PRIVATE_KEY,
    SERVER_PUBLIC_KEY,
    REDIRECT_URL_TO_LOUIS_FRONTEND,
)

# A basic in-memory store for simplicity;
TOKEN_BLACKLIST = set()

logging.basicConfig(level=logging.DEBUG)

# Initialize Quart application
app = Quart(__name__)

# Allow CORS for your Quart app
app = cors(app, allow_origin=ALLOWED_ORIGINS_LIST, allow_credentials=True)

# Configuration for JWT and session settings
# Fetch secret key or generate a new one if not available
SECRET_KEY = os.getenv("SECRET_KEY", str(uuid.uuid4()))
# Set secret key configurations for JWT and Quart session
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["SECRET_KEY"] = SECRET_KEY

# Configure JWT expiration from environment variable with default of 30 minutes
jwt_expiration_minutes = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 30))

# Configure session lifetime from environment variable with default of 30 minutes
session_lifetime_minutes = int(os.environ.get("SESSION_LIFETIME_MINUTES", 30))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=session_lifetime_minutes)

# Configure session cookie to be secure (sent over HTTPS only)
app.config["SESSION_COOKIE_SECURE"] = True

# Initialize JWT Manager with the app
jwt = JWTManager(app)

# Configure Quart-Session
app.config["SESSION_TYPE"] = os.getenv("SESSION_TYPE", default="filesystem")
Session(app)

# Register custom error handlers for the Quart app
register_error_handlers(app)


@app.before_request
async def log_request_info():
    """Log incoming request headers and body for debugging purposes."""
    app.logger.debug("Headers: %s", request.headers)
    app.logger.debug("Body: %s", await request.get_data())


@app.route("/health")
async def health_check():
    return "ok", 200


@app.route("/authenticate", methods=["GET", "POST"])
async def authenticate():
    """
    Authenticate the client request based on various possible inputs.

    This endpoint can handle three types of requests:
    1. If the request contains both a valid client JWT and an email:
        - Validates the provided email.
        - Generates a verification token and sends a verification email to the provided address.
    2. If the request only contains a valid client JWT without an email:
        - Redirects the user to the Louis login frontend.
    3. If client JWT decoding fails:
        - Attempts to decode using the verification token method, to validate a user attempting
          to confirm their email.

    Returns:
        JSON response or redirect, depending on the provided inputs and their validation.
    """
    app.logger.debug("Entering authenticate route")

    try:
        clientapp_token = request.args.get("token")
        clientapp_decoded_token = decode_client_jwt_token(
            clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY
        )

        # If the request contains an email parameter provided by the user.
        if clientapp_decoded_token and request.is_json:
            # Validate email.
            email = validate_email_from_request((await request.get_json()).get("email"))
            # Generate token expiration timestamp.
            # Construct the verification URL which includes the new JWT token.
            verification_url = generate_email_verification_token(
                email,
                clientapp_decoded_token["redirect_url"],
                jwt_expiration_minutes,
                SERVER_PRIVATE_KEY,
            )

            # Send an email with verification url
            app.add_background_task(
                send_email,
                MEMBRANE_BACKEND_COMM_CONNECTION_STRING,
                MEMBRANE_BACKEND_SENDER_EMAIL,
                email,
                "Please Verify Your Email Address",
                verification_url,
                app.logger,
            )

            return (
                jsonify({"message": "Valid email address. Email sent with JWT link."}),
                200,
            )

        # Redirect user if they reload the link without providing an email.
        return login_redirect_with_client_jwt(
            clientapp_token,
            CLIENT_PUBLIC_KEYS_DIRECTORY,
            REDIRECT_URL_TO_LOUIS_FRONTEND,
        )

    except (JWTError, EmailError) as error:
        app.logger.error("Error occurred: %s\n%s", error, traceback.format_exc())
        try:
            app.logger.info(
                "Attempting to redirect_to_client_app_using_verification_token"
            )
            return redirect_to_client_app_using_verification_token(
                clientapp_token, SERVER_PUBLIC_KEY, TOKEN_BLACKLIST
            )
        except JWTError as inner_error:
            app.logger.error(
                "Secondary error encountered during redirect. Type of error: %s\n%s",
                type(inner_error),
                traceback.format_exc(),
            )
            # TODO: Redirect to Louis main site if token is invalid.

    return (
        jsonify({"error": "Invalid request method"}),
        405,
    )  # 405 is for Method Not Allowed


if __name__ == "__main__":
    app.run(debug=True)
