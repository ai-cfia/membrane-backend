"""
Pytest configuration and shared fixtures for test setup.
"""
import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

load_dotenv(".env.tests")

# Import the Quart application instance
from app import app as quart_app  # noqa: E402
from generate_jwt import generate_jwt  # noqa: E402
from jwt_utils import generate_email_verification_token  # noqa: E402


@pytest.fixture
def app():
    """Quart application fixture for the tests."""
    quart_app.config["SESSION_TYPE"] = os.getenv("MEMBRANE_SESSION_TYPE")
    quart_app.config["TESTING"] = True
    quart_app.config["SERVER_NAME"] = "whaterver"
    yield quart_app
    # # pylint: disable=redefined-outer-name


@pytest.fixture
def test_client(app):
    """Test client fixture for the tests."""
    yield quart_app.test_client()


@pytest.fixture(scope="session")
def test_private_key():
    """Fixture to read and provide the private key."""
    with open(os.getenv("MEMBRANE_TEST_APP_PRIVATE_KEY", ""), "rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def azure_conn_string():
    return os.getenv("MEMBRANE_COMM_CONNECTION_STRING")


@pytest.fixture(scope="session")
def sender_email():
    return os.getenv("MEMBRANE_SENDER_EMAIL")


@pytest.fixture(scope="session")
def invalid_emails():
    return os.getenv("MEMBRANE_INVALID_EMAILS").split(",")


@pytest.fixture(scope="session")
def receiver_email():
    return os.getenv("MEMBRANE_RECEIVER_EMAIL")


@pytest.fixture(scope="session")
def email_subject():
    return os.getenv("MEMBRANE_EMAIL_SUBJECT")


@pytest.fixture(scope="session")
def email_body():
    return os.getenv("MEMBRANE_EMAIL_BODY")


@pytest.fixture(scope="session")
def data_field():
    return os.getenv("MEMBRANE_DATA_FIELD")


@pytest.fixture(scope="session")
def data():
    return os.getenv("MEMBRANE_DATA")


@pytest.fixture(scope="session")
def app_id_field():
    return os.getenv("MEMBRANE_APP_ID_FIELD")


@pytest.fixture(scope="session")
def app_id():
    return os.getenv("MEMBRANE_APP_ID")


@pytest.fixture(scope="session")
def redirect_url_field():
    return os.getenv("MEMBRANE_REDIRECT_URL_FIELD")


@pytest.fixture(scope="session")
def redirect_url():
    return os.getenv("MEMBRANE_REDIRECT_URL")


@pytest.fixture(scope="session")
def test_app_public_key_dir():
    return Path(os.getenv("MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY"))


@pytest.fixture(scope="session")
def expiration_field():
    return os.getenv("MEMBRANE_EXPIRATION_FIELD")


@pytest.fixture
def payload(
    data_field,
    data,
    app_id_field,
    app_id,
    redirect_url_field,
    redirect_url,
):
    """Test client fixture for the tests."""
    return {
        data_field: data,
        app_id_field: app_id,
        redirect_url_field: redirect_url,
    }


@pytest.fixture
def sample_jwt_token(generate_jwt_token, payload):
    """Fixture to generate a sample JWT token for testing."""
    return generate_jwt_token(payload)


@pytest.fixture
def generate_jwt_token(test_private_key):
    """Fixture to generate JWT tokens for testing purposes."""

    def _generator(payload, headers=None):
        return generate_jwt(payload, test_private_key, headers=headers)

    return _generator


@pytest.fixture
async def sample_verification_token(app):
    """Fixture to generate a sample email verification token for testing."""
    async with app.app_context():
        verification_url = generate_email_verification_token(
            os.getenv("MEMBRANE_RECEIVER_EMAIL"),
            os.getenv("MEMBRANE_FRONTEND"),
            int(os.getenv("MEMBRANE_JWT_EXPIRE_SECONDS")),
            Path(os.getenv("MEMBRANE_SERVER_PRIVATE_KEY")),
        )
    return verification_url
