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
            os.getenv("MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY", "keys/public_keys")
        ),
        server_public_key=Path(os.getenv("MEMBRANE_SERVER_PUBLIC_KEY", "")),
        server_private_key=Path(os.getenv("MEMBRANE_SERVER_PRIVATE_KEY", "")),
        app_id_field=os.getenv("MEMBRANE_APP_ID_FIELD", ""),
        redirect_url_field=os.getenv("MEMBRANE_REDIRECT_URL_FIELD", ""),
        expiration_field=os.getenv("MEMBRANE_EXPIRATION_FIELD", ""),
        algorithm=os.getenv("MEMBRANE_ENCODE_ALGORITHM", ""),
        data_field=os.getenv("MEMBRANE_DATA_FIELD", ""),
        token_type=os.getenv("MEMBRANE_TOKEN_TYPE", ""),
        jwt_access_token_expire_seconds=int(
            os.getenv("MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS", 30 * 60)
        ),
        jwt_expire_seconds=int(os.getenv("MEMBRANE_JWT_EXPIRE_SECONDS", 30 * 60)),
        token_blacklist=set(os.getenv("MEMBRANE_TOKEN_BLACKLIST", "").split(",")),
    )

    email_config = EmailConfig(
        email_client=EmailClient.from_connection_string(
            os.getenv("MEMBRANE_COMM_CONNECTION_STRING", "")
        ),
        sender_email=os.getenv("MEMBRANE_SENDER_EMAIL", ""),
        subject=os.getenv("MEMBRANE_EMAIL_SUBJECT", ""),
        html_content=os.getenv("MEMBRANE_EMAIL_SEND_HTML_TEMPLATE", ""),
        poller_wait_time=int(os.getenv("MEMBRANE_EMAIL_SEND_POLLER_WAIT_SECONDS", 10)),
        timeout=int(os.getenv("MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS", 180)),
        validation_pattern=os.getenv("MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN", ""),
        email_send_success=os.getenv("MEMBRANE_EMAIL_SEND_SUCCESS", ""),
    )

    app = Quart(__name__)

    app.config.update(
        {
            "JWT_CONFIG": jwt_config,
            "EMAIL_CONFIG": email_config,
            "MEMBRANE_ALLOWED_ORIGINS": os.getenv(
                "MEMBRANE_ALLOWED_ORIGINS", "*"
            ).split(","),
            "MEMBRANE_LOGGING_LEVEL": os.getenv("MEMBRANE_LOGGING_LEVEL", "DEBUG"),
            "MEMBRANE_LOGGING_FORMAT": os.getenv("MEMBRANE_LOGGING_FORMAT", ""),
            "MEMBRANE_HEALTH_MESSAGE": os.getenv("MEMBRANE_HEALTH_MESSAGE", "Ok"),
            "MEMBRANE_FRONTEND": os.getenv("MEMBRANE_FRONTEND", ""),
            "SECRET_KEY": os.getenv("MEMBRANE_SECRET_KEY", ""),
            "PERMANENT_SESSION_LIFETIME": timedelta(
                seconds=int(os.getenv("MEMBRANE_SESSION_LIFETIME_SECONDS", 30 * 60))
            ),
            "SESSION_COOKIE_SECURE": os.getenv(
                "MEMBRANE_SESSION_COOKIE_SECURE", "true"
            ).lower()
            == "true",
            "SESSION_TYPE": os.getenv("MEMBRANE_SESSION_TYPE", "filesystem"),
            "MEMBRANE_GENERIC_500_ERROR_FIELD": os.getenv(
                "MEMBRANE_GENERIC_500_ERROR_FIELD", ""
            ),
            "MEMBRANE_GENERIC_500_ERROR": os.getenv("MEMBRANE_GENERIC_500_ERROR", ""),
        }
    )

    validate_environment_settings(
        jwt_config.client_public_keys_folder,
        jwt_config.server_private_key,
        jwt_config.server_public_key,
        app.config["MEMBRANE_FRONTEND"],
    )

    app = cors(
        app, allow_origin=app.config["MEMBRANE_ALLOWED_ORIGINS"], allow_credentials=True
    )
    logging.basicConfig(
        format=app.config["MEMBRANE_LOGGING_FORMAT"],
        level=getattr(logging, app.config["MEMBRANE_LOGGING_LEVEL"]),
    )
    Session(app)
    return app
