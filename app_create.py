import logging
import os
from datetime import timedelta
from pathlib import Path

from azure.communication.email import EmailClient
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
from quart_session import Session

from emails import EmailConfig
from environment_validation import validate_environment_settings
from jwt_utils import JWTConfig


def create_app():
    load_dotenv()

    jwt_config = JWTConfig(
        client_public_keys_folder=Path(
            os.getenv("MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY")
        ),
        server_public_key=Path(os.getenv("MEMBRANE_SERVER_PUBLIC_KEY")),
        server_private_key=Path(os.getenv("MEMBRANE_SERVER_PRIVATE_KEY")),
        app_id_field=os.getenv("MEMBRANE_APP_ID_FIELD", "app_id"),
        redirect_url_field=os.getenv("MEMBRANE_REDIRECT_URL_FIELD", "redirect_url"),
        expiration_field=os.getenv("MEMBRANE_EXPIRATION_FIELD", "exp"),
        algorithm=os.getenv("MEMBRANE_ENCODE_ALGORITHM", "RS256"),
        data_field=os.getenv("MEMBRANE_DATA_FIELD", "data"),
        token_type=os.getenv("MEMBRANE_TOKEN_TYPE", "JWT"),
        jwt_access_token_expire_seconds=int(
            os.getenv("MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS", 300)
        ),
        jwt_expire_seconds=int(os.getenv("MEMBRANE_JWT_EXPIRE_SECONDS", 300)),
        token_blacklist=set(os.getenv("MEMBRANE_TOKEN_BLACKLIST", "").split(",")),
    )

    email_config = EmailConfig(
        email_client=EmailClient.from_connection_string(
            os.getenv("MEMBRANE_COMM_CONNECTION_STRING")
        ),
        sender_email=os.getenv("MEMBRANE_SENDER_EMAIL"),
        subject=os.getenv("MEMBRANE_EMAIL_SUBJECT", "Please Verify You Email Address"),
        html_content=os.getenv(
            "MEMBRANE_EMAIL_SEND_HTML_TEMPLATE", "<html><h1>{}</h1></html>"
        ),
        poller_wait_time=int(os.getenv("MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME", 2)),
        timeout=int(os.getenv("MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS", 20)),
        validation_pattern=os.getenv(
            "MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN",
            "^[a-zA-Z0-9._%+-]+@(?:gc.ca|outlook.com)$",
        ),
        email_send_success=os.getenv(
            "MEMBRANE_EMAIL_SEND_SUCCESS",
            "Valid email address, Email sent with JWT link",
        ),
    )

    app = Quart(__name__)

    app.config.update(
        {
            "JWT_CONFIG": jwt_config,
            "EMAIL_CONFIG": email_config,
            "MEMBRANE_CORS_ALLOWED_ORIGINS": os.getenv(
                "MEMBRANE_CORS_ALLOWED_ORIGINS"
            ).split(","),
            "MEMBRANE_LOGGING_LEVEL": os.getenv("MEMBRANE_LOGGING_LEVEL", "DEBUG"),
            "MEMBRANE_LOGGING_FORMAT": os.getenv(
                "MEMBRANE_LOGGING_FORMAT",
                "[%(asctime)s] [%(levelname)s] "
                "[%(filename)s:%(lineno)d:%(funcName)s] - %(message)s",
            ),
            "MEMBRANE_HEALTH_MESSAGE": os.getenv("MEMBRANE_HEALTH_MESSAGE", "Ok"),
            "MEMBRANE_FRONTEND": os.getenv("MEMBRANE_FRONTEND"),
            "SECRET_KEY": os.getenv("MEMBRANE_SECRET_KEY"),
            "PERMANENT_SESSION_LIFETIME": timedelta(
                seconds=int(os.getenv("MEMBRANE_SESSION_LIFETIME_SECONDS", 300))
            ),
            "SESSION_COOKIE_SECURE": os.getenv(
                "MEMBRANE_SESSION_COOKIE_SECURE", "true"
            ).lower()
            == "true",
            "SESSION_TYPE": os.getenv("MEMBRANE_SESSION_TYPE", "null"),
            "MEMBRANE_GENERIC_500_ERROR_FIELD": os.getenv(
                "MEMBRANE_GENERIC_500_ERROR_FIELD", "error"
            ),
            "MEMBRANE_GENERIC_500_ERROR": os.getenv(
                "MEMBRANE_GENERIC_500_ERROR",
                "An unexpected error occurred. Please try again later.",
            ),
        }
    )

    validate_environment_settings(
        jwt_config.client_public_keys_folder,
        jwt_config.server_private_key,
        jwt_config.server_public_key,
        app.config["MEMBRANE_FRONTEND"],
    )

    app = cors(
        app,
        allow_origin=app.config["MEMBRANE_CORS_ALLOWED_ORIGINS"],
        allow_credentials=True,
    )
    logging.basicConfig(
        format=app.config["MEMBRANE_LOGGING_FORMAT"],
        level=getattr(logging, app.config["MEMBRANE_LOGGING_LEVEL"]),
    )
    Session(app)
    return app
