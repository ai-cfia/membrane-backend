import logging
import os
from datetime import timedelta
from pathlib import Path

from azure.communication.email import EmailClient
from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
from quart_session import Session

import emails
import jwt_utils
from environment_validation import validate_environment_settings

DEFAULT_MEMBRANE_LOGGING_LEVEL = "DEBUG"
DEFAULT_MEMBRANE_LOGGING_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s"
)
DEFAULT_MEMBRANE_HEALTH_MESSAGE = "ok"
DEFAULT_MEMBRANE_SESSION_LIFETIME_SECONDS = 300
DEFAULT_MEMBRANE_SESSION_COOKIE_SECURE = "true"
DEFAULT_MEMBRANE_SESSION_TYPE = "null"
DEFAULT_MEMBRANE_GENERIC_500_ERROR_FIELD = "error"
DEFAULT_MEMBRANE_GENERIC_500_ERROR = (
    "An unexpected error occurred. Please try again later."
)


def create_app():
    load_dotenv()

    jwt_config = jwt_utils.JWTConfig(
        client_public_keys_folder=Path(
            os.getenv(
                "MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY",
                jwt_utils.DEFAULT_CLIENT_PUBLIC_KEYS_DIRECTORY,
            )
        ),
        server_public_key=Path(
            os.getenv("MEMBRANE_SERVER_PUBLIC_KEY", jwt_utils.DEFAULT_SERVER_PUBLIC_KEY)
        ),
        server_private_key=Path(
            os.getenv(
                "MEMBRANE_SERVER_PRIVATE_KEY", jwt_utils.DEFAULT_SERVER_PRIVATE_KEY
            )
        ),
        app_id_field=os.getenv("MEMBRANE_APP_ID_FIELD", jwt_utils.DEFAULT_APP_ID_FIELD),
        redirect_url_field=os.getenv(
            "MEMBRANE_REDIRECT_URL_FIELD", jwt_utils.DEFAULT_REDIRECT_URL_FIELD
        ),
        algorithm=os.getenv(
            "MEMBRANE_ENCODE_ALGORITHM", jwt_utils.DEFAULT_ENCODE_ALGORITHM
        ),
        data_field=os.getenv("MEMBRANE_DATA_FIELD", jwt_utils.DEFAULT_DATA_FIELD),
        jwt_access_token_expire_seconds=int(
            os.getenv(
                "MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS",
                jwt_utils.DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
            )
        ),
        jwt_expire_seconds=int(
            os.getenv(
                "MEMBRANE_JWT_EXPIRE_SECONDS", jwt_utils.DEFAULT_JWT_EXPIRE_SECONDS
            )
        ),
        token_blacklist=set(
            os.getenv(
                "MEMBRANE_TOKEN_BLACKLIST", jwt_utils.DEFAULT_TOKEN_BLACKLIST
            ).split(",")
        ),
    )
    email_config = emails.EmailConfig(
        email_client=EmailClient.from_connection_string(
            os.getenv("MEMBRANE_COMM_CONNECTION_STRING")
        ),
        sender_email=os.getenv("MEMBRANE_SENDER_EMAIL"),
        subject=os.getenv("MEMBRANE_EMAIL_SUBJECT", emails.DEFAULT_EMAIL_SUBJECT),
        html_content=os.getenv(
            "MEMBRANE_EMAIL_SEND_HTML_TEMPLATE", emails.DEFAULT_HTML_CONTENT
        ),
        poller_wait_seconds=int(
            os.getenv(
                "MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME",
                emails.DEFAULT_POLLER_WAIT_SECONDS,
            )
        ),
        timeout=int(
            os.getenv(
                "MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS", emails.DEFAULT_TIMEOUT_SECONDS
            )
        ),
        validation_pattern=os.getenv(
            "MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN",
            emails.DEFAULT_VALIDATION_PATTERN,
        ),
        email_send_success=os.getenv(
            "MEMBRANE_EMAIL_SEND_SUCCESS",
            emails.DEFAULT_SUCCESS_MESSAGE,
        ),
    )

    app = Quart(__name__)

    app.config.update(
        {
            "MEMBRANE_LOGGING_LEVEL": os.getenv(
                "MEMBRANE_LOGGING_LEVEL", DEFAULT_MEMBRANE_LOGGING_LEVEL
            ),
            "MEMBRANE_LOGGING_FORMAT": os.getenv(
                "MEMBRANE_LOGGING_FORMAT", DEFAULT_MEMBRANE_LOGGING_FORMAT
            ),
            "MEMBRANE_HEALTH_MESSAGE": os.getenv(
                "MEMBRANE_HEALTH_MESSAGE", DEFAULT_MEMBRANE_HEALTH_MESSAGE
            ),
            "PERMANENT_SESSION_LIFETIME": timedelta(
                seconds=int(
                    os.getenv(
                        "MEMBRANE_SESSION_LIFETIME_SECONDS",
                        DEFAULT_MEMBRANE_SESSION_LIFETIME_SECONDS,
                    )
                )
            ),
            "SESSION_COOKIE_SECURE": os.getenv(
                "MEMBRANE_SESSION_COOKIE_SECURE", DEFAULT_MEMBRANE_SESSION_COOKIE_SECURE
            ).lower()
            == "true",
            "SESSION_TYPE": os.getenv(
                "MEMBRANE_SESSION_TYPE", DEFAULT_MEMBRANE_SESSION_TYPE
            ),
            "MEMBRANE_GENERIC_500_ERROR_FIELD": os.getenv(
                "MEMBRANE_GENERIC_500_ERROR_FIELD",
                DEFAULT_MEMBRANE_GENERIC_500_ERROR_FIELD,
            ),
            "MEMBRANE_GENERIC_500_ERROR": os.getenv(
                "MEMBRANE_GENERIC_500_ERROR", DEFAULT_MEMBRANE_GENERIC_500_ERROR
            ),
            "JWT_CONFIG": jwt_config,
            "EMAIL_CONFIG": email_config,
            "MEMBRANE_CORS_ALLOWED_ORIGINS": os.getenv(
                "MEMBRANE_CORS_ALLOWED_ORIGINS"
            ).split(","),
            "MEMBRANE_FRONTEND": os.getenv("MEMBRANE_FRONTEND"),
            "SECRET_KEY": os.getenv("MEMBRANE_SECRET_KEY"),
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
