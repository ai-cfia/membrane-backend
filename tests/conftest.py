"""
Pytest configuration and shared fixtures for test setup.
"""
import os
from datetime import datetime, timedelta
from pathlib import Path

import jwt
import pytest
from dotenv import load_dotenv

load_dotenv(".env.tests")

# Import the Quart application instance
from app import app as quart_app  # noqa: E402
from jwt_utils import generate_email_verification_token  # noqa: E402

SERVER_PRIVATE_KEY = Path("tests/server_private_key/server_private_key.pem")


@pytest.fixture
def app():
    """Quart application fixture for the tests."""
    quart_app.config["TESTING"] = True
    quart_app.config["SERVER_NAME"] = "login.example.com"
    quart_app.config["MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY"] = Path(
        "tests/client_public_keys"
    )
    quart_app.config["MEMBRANE_SERVER_PRIVATE_KEY"] = SERVER_PRIVATE_KEY
    quart_app.config["MEMBRANE_SERVER_PUBLIC_KEY"] = Path(
        "tests/server_public_key/server_public_key.pem"
    )
    yield quart_app
    # # pylint: disable=redefined-outer-name


@pytest.fixture
def test_client(app):
    """Test client fixture for the tests."""
    yield quart_app.test_client()


@pytest.fixture(scope="session")
def client_private_key():
    """Fixture to read and provide the private key."""
    with open("tests/client_private_keys/testapp1_private_key.pem", "rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def data_field():
    return quart_app.config["MEMBRANE_DATA_FIELD"]


@pytest.fixture(scope="session")
def app_id_field():
    return quart_app.config["MEMBRANE_APP_ID_FIELD"]


@pytest.fixture(scope="session")
def redirect_url_field():
    return quart_app.config["MEMBRANE_REDIRECT_URL_FIELD"]


@pytest.fixture(scope="session")
def expiration_field():
    return quart_app.config["MEMBRANE_EXPIRATION_FIELD"]


@pytest.fixture(scope="session")
def algorithm():
    return quart_app.config["MEMBRANE_ENCODE_ALGORITHM"]


@pytest.fixture(scope="session")
def token_type():
    return quart_app.config["MEMBRANE_TOKEN_TYPE"]


@pytest.fixture
def payload(
    data_field,
    app_id_field,
    redirect_url_field,
):
    """Test client fixture for the tests."""
    return {
        data_field: "test_data",
        app_id_field: "testapp1",
        redirect_url_field: "www.example.com",
    }


@pytest.fixture
def sample_jwt_token(
    generate_jwt_token,
    payload,
    expiration_field,
    algorithm,
    token_type,
    app_id_field,
):
    """Fixture to generate a sample JWT token for testing."""
    return generate_jwt_token(
        payload, expiration_field, algorithm, token_type, app_id_field, "testapp1"
    )


@pytest.fixture
def generate_jwt_token(client_private_key):
    """Fixture to generate JWT tokens for testing purposes."""

    def _generator(
        payload, expiration_field, algorithm, token_type, app_id_field, app_id
    ):
        if expiration_field not in payload:
            expiration_seconds = datetime.utcnow() + timedelta(seconds=5 * 60)
            payload[expiration_field] = int(expiration_seconds.timestamp())
        headers = {"alg": algorithm, "typ": token_type, app_id_field: app_id}
        return jwt.encode(payload, client_private_key, algorithm, headers)

    return _generator


@pytest.fixture
async def sample_verification_token(app):
    """Fixture to generate a sample email verification token for testing."""
    async with app.app_context():
        verification_url = generate_email_verification_token(
            "test@inspection.gc.ca",
            "https://www.example.com/",
            int(5 * 60),
            SERVER_PRIVATE_KEY,
        )
    return verification_url
