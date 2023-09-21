import logging
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from quart import Quart
from quart_cors import cors
from quart_session import Session

from environment_validation import validate_environment_settings


def create_app():
    """
    Configure and return a Quart application instance with settings from environment
    variables.
    """
    load_dotenv()

    app = Quart(__name__)

    app.config.update(
        {
            "MEMBRANE_ALLOWED_ORIGINS": os.getenv(
                "MEMBRANE_ALLOWED_ORIGINS", "*"
            ).split(","),
            "MEMBRANE_FRONTEND": os.getenv("MEMBRANE_FRONTEND", ""),
            "SECRET_KEY": os.getenv("MEMBRANE_SECRET_KEY", ""),
            "MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY": Path(
                os.getenv("MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY", "keys/public_keys")
            ),
            "MEMBRANE_SERVER_PRIVATE_KEY": Path(
                os.getenv("MEMBRANE_SERVER_PRIVATE_KEY", "")
            ),
            "MEMBRANE_SERVER_PUBLIC_KEY": Path(
                os.getenv("MEMBRANE_SERVER_PUBLIC_KEY", "")
            ),
            "MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS": int(
                os.getenv("MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS", 30 * 60)
            ),
            "MEMBRANE_JWT_EXPIRE_SECONDS": int(
                os.getenv("MEMBRANE_JWT_EXPIRE_SECONDS", 30 * 60)
            ),
            "PERMANENT_SESSION_LIFETIME": timedelta(
                seconds=int(os.getenv("MEMBRANE_SESSION_LIFETIME_SECONDS", 30 * 60))
            ),
            "SESSION_COOKIE_SECURE": os.getenv(
                "MEMBRANE_SESSION_COOKIE_SECURE", "true"
            ).lower()
            == "true",
            "SESSION_TYPE": os.getenv("MEMBRANE_SESSION_TYPE", "filesystem"),
            "MEMBRANE_TOKEN_BLACKLIST": set(
                os.getenv("TOKEN_BLACKLIST", "").split(",")
            ),
            "MEMBRANE_LOGGING_LEVEL": os.getenv("MEMBRANE_LOGGING_LEVEL", "DEBUG"),
            "MEMBRANE_ALLOWED_EMAIL_DOMAINS": os.getenv(
                "MEMBRANE_ALLOWED_EMAIL_DOMAINS", ""
            ),
            "MEMBRANE_COMM_CONNECTION_STRING": os.getenv(
                "MEMBRANE_COMM_CONNECTION_STRING", ""
            ),
            "MEMBRANE_SENDER_EMAIL": os.getenv("MEMBRANE_SENDER_EMAIL", ""),
            "MEMBRANE_EMAIL_SUBJECT": os.getenv("MEMBRANE_EMAIL_SUBJECT", ""),
            "MEMBRABE_EMAIL_SEND_SUCCESS": os.getenv("MEMBRABE_EMAIL_SEND_SUCCESS", ""),
            "MEMBRANE_EMAIL_SEND_HTLM_TEMPLATE": os.getenv(
                "MEMBRANE_EMAIL_SEND_HTLM_TEMPLATE", ""
            ),
            "MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME": int(
                os.getenv("MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME", "")
            ),
        }
    )

    validate_environment_settings(
        app.config["MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY"],
        app.config["MEMBRANE_SERVER_PRIVATE_KEY"],
        app.config["MEMBRANE_SERVER_PUBLIC_KEY"],
        app.config["MEMBRANE_FRONTEND"],
    )

    app = cors(
        app, allow_origin=app.config["MEMBRANE_ALLOWED_ORIGINS"], allow_credentials=True
    )

    logging.basicConfig(level=getattr(logging, app.config["MEMBRANE_LOGGING_LEVEL"]))

    Session(app)
    return app
