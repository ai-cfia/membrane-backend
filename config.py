import os
from dataclasses import dataclass
from pathlib import Path

from azure.communication.email import EmailClient
from dotenv import load_dotenv

DEFAULT_LOGGING_LEVEL = "DEBUG"
DEFAULT_LOGGING_FORMAT = (
    "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s"
)
DEFAULT_HEALTH_MESSAGE = "ok"
DEFAULT_SESSION_LIFETIME_SECONDS = 300
DEFAULT_SESSION_COOKIE_SECURE = "true"
DEFAULT_SESSION_TYPE = "null"
DEFAULT_GENERIC_500_ERROR_FIELD = "error"
DEFAULT_GENERIC_500_ERROR = "An unexpected error occurred. Please try again later."


DEFAULT_CLIENT_PUBLIC_KEYS_DIRECTORY = "./keys/client"
DEFAULT_SERVER_PUBLIC_KEY = "./keys/server_public.pem"
DEFAULT_SERVER_PRIVATE_KEY = "./keys/server_private.pem"
DEFAULT_APP_ID_FIELD = "app_id"
DEFAULT_REDIRECT_URL_FIELD = "redirect_url"
DEFAULT_ENCODE_ALGORITHM = "RS256"
DEFAULT_DATA_FIELD = "data"
DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_SECONDS = 300
DEFAULT_JWT_EXPIRE_SECONDS = 300
DEFAULT_TOKEN_BLACKLIST = ""


DEFAULT_HTML_CONTENT = "<html><h1>{}</h1></html>"
DEFAULT_POLLER_WAIT_SECONDS = 10
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_VALIDATION_PATTERN = (
    "^[a-zA-Z0-9._+]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$"
)
DEFAULT_SUCCESS_MESSAGE = "Valid email address, Email sent with JWT link"
DEFAULT_EMAIL_SUBJECT = "Please Verify You Email Address"


load_dotenv()


@dataclass
class JWTConfig:
    client_public_keys_folder = Path(
        os.getenv(
            "MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY",
            DEFAULT_CLIENT_PUBLIC_KEYS_DIRECTORY,
        )
    )
    server_public_key = Path(
        os.getenv("MEMBRANE_SERVER_PUBLIC_KEY", DEFAULT_SERVER_PUBLIC_KEY)
    )
    server_private_key = Path(
        os.getenv("MEMBRANE_SERVER_PRIVATE_KEY", DEFAULT_SERVER_PRIVATE_KEY)
    )
    app_id_field = os.getenv("MEMBRANE_APP_ID_FIELD", DEFAULT_APP_ID_FIELD)
    redirect_url_field = os.getenv(
        "MEMBRANE_REDIRECT_URL_FIELD", DEFAULT_REDIRECT_URL_FIELD
    )
    algorithm = os.getenv("MEMBRANE_ENCODE_ALGORITHM", DEFAULT_ENCODE_ALGORITHM)
    data_field = os.getenv("MEMBRANE_DATA_FIELD", DEFAULT_DATA_FIELD)
    jwt_access_token_expire_seconds = int(
        os.getenv(
            "MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS",
            DEFAULT_JWT_ACCESS_TOKEN_EXPIRE_SECONDS,
        )
    )
    jwt_expire_seconds = int(
        os.getenv("MEMBRANE_JWT_EXPIRE_SECONDS", DEFAULT_JWT_EXPIRE_SECONDS)
    )
    token_blacklist = set(
        os.getenv("MEMBRANE_TOKEN_BLACKLIST", DEFAULT_TOKEN_BLACKLIST).split(",")
    )
    token_type: str = "JWT"


@dataclass
class EmailConfig:
    email_client = EmailClient.from_connection_string(
        os.getenv("MEMBRANE_COMM_CONNECTION_STRING")
    )
    sender_email = os.getenv("MEMBRANE_SENDER_EMAIL")
    subject = os.getenv("MEMBRANE_EMAIL_SUBJECT", DEFAULT_EMAIL_SUBJECT)
    html_content = os.getenv("MEMBRANE_EMAIL_SEND_HTML_TEMPLATE", DEFAULT_HTML_CONTENT)
    poller_wait_seconds = int(
        os.getenv(
            "MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME",
            DEFAULT_POLLER_WAIT_SECONDS,
        )
    )
    timeout = int(
        os.getenv("MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    )
    validation_pattern = os.getenv(
        "MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN",
        DEFAULT_VALIDATION_PATTERN,
    )
    email_send_success = os.getenv(
        "MEMBRANE_EMAIL_SEND_SUCCESS",
        DEFAULT_SUCCESS_MESSAGE,
    )


@dataclass
class AppConfig:
    LOGGING_LEVEL = os.getenv("MEMBRANE_LOGGING_LEVEL", DEFAULT_LOGGING_LEVEL)
    LOGGING_FORMAT = os.getenv("MEMBRANE_LOGGING_FORMAT", DEFAULT_LOGGING_FORMAT)
    HEALTH_MESSAGE = os.getenv("MEMBRANE_HEALTH_MESSAGE", DEFAULT_HEALTH_MESSAGE)
    PERMANENT_SESSION_LIFETIME = os.getenv(
        "MEMBRANE_SESSION_LIFETIME_SECONDS", DEFAULT_SESSION_LIFETIME_SECONDS
    )
    SESSION_COOKIE_SECURE = (
        os.getenv(
            "MEMBRANE_SESSION_COOKIE_SECURE", DEFAULT_SESSION_COOKIE_SECURE
        ).lower()
        == "true"
    )
    SESSION_TYPE = os.getenv("MEMBRANE_SESSION_TYPE", DEFAULT_SESSION_TYPE)
    GENERIC_500_ERROR_FIELD = os.getenv(
        "MEMBRANE_GENERIC_500_ERROR_FIELD", DEFAULT_GENERIC_500_ERROR_FIELD
    )
    GENERIC_500_ERROR = os.getenv(
        "MEMBRANE_GENERIC_500_ERROR", DEFAULT_GENERIC_500_ERROR
    )
    CORS_ALLOWED_ORIGINS = os.getenv("MEMBRANE_CORS_ALLOWED_ORIGINS").split(",")
    MEMBRANE_FRONTEND = os.getenv("MEMBRANE_FRONTEND")
    SECRET_KEY = os.getenv("MEMBRANE_SECRET_KEY")
    JWT_CONFIG = JWTConfig()
    EMAIL_CONFIG = EmailConfig()
