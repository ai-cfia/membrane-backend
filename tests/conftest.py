"""
Pytest configuration and shared fixtures for test setup.
"""
from datetime import datetime, timedelta
from pathlib import Path

import jwt
import pytest
from dotenv import load_dotenv

from emails import EmailConfig

load_dotenv(".env.tests")

# Import the Quart application instance
from app import app as quart_app  # noqa: E402
from jwt_utils import JWTConfig, generate_email_verification_token  # noqa: E402


@pytest.fixture
def app():
    """Quart application fixture for the tests."""
    jwt_config = JWTConfig(
        client_public_keys_folder=Path("tests/client_public_keys"),
        server_public_key=Path("tests/server_public_key/server_public_key.pem"),
        server_private_key=Path("tests/server_private_key/server_private_key.pem"),
        app_id_field="app_id",
        redirect_url_field="redirect_url",
        expiration_field="exp",
        algorithm="RS256",
        data_field="data",
        jwt_access_token_expire_seconds=300,
        jwt_expire_seconds=300,
        token_blacklist=set(),
        token_type="JWT",
    )
    email_config = EmailConfig(
        email_client=None,
        sender_email="",
        subject="Please Verify You Email Address",
        validation_pattern="^[a-zA-Z0-9._%+-]+@(?:gc.ca|canada.ca|inspection.gc.ca)$",
        email_send_success="Valid email address, Email sent with JWT link",
        html_content="<html><h1>{}</h1></html>",
        poller_wait_time=2,
        timeout=20,
    )
    quart_app.config["JWT_CONFIG"] = jwt_config
    quart_app.config["EMAIL_CONFIG"] = email_config
    quart_app.config["TESTING"] = True
    quart_app.config["SERVER_NAME"] = "login.example.com"
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
def jwt_config():
    return quart_app.config["JWT_CONFIG"]


@pytest.fixture(scope="session")
def email_config():
    return quart_app.config["EMAIL_CONFIG"]


@pytest.fixture
def payload(jwt_config: JWTConfig):
    """Test client fixture for the tests."""
    return {
        jwt_config.data_field: "test_data",
        jwt_config.app_id_field: "testapp1",
        jwt_config.redirect_url_field: "www.example.com",
    }


@pytest.fixture
def sample_jwt_token(generate_jwt_token, payload, jwt_config: JWTConfig):
    """Fixture to generate a sample JWT token for testing."""
    return generate_jwt_token(payload, jwt_config, "testapp1")


@pytest.fixture
def generate_jwt_token(client_private_key):
    """Fixture to generate JWT tokens for testing purposes."""

    def _generator(payload, jwt_config: JWTConfig, app_id):
        if jwt_config.expiration_field not in payload:
            expiration_seconds = datetime.utcnow() + timedelta(seconds=5 * 60)
            payload[jwt_config.expiration_field] = int(expiration_seconds.timestamp())
        headers = {
            "alg": jwt_config.algorithm,
            "typ": jwt_config.token_type,
            jwt_config.app_id_field: app_id,
        }
        return jwt.encode(payload, client_private_key, jwt_config.algorithm, headers)

    return _generator


@pytest.fixture
async def sample_verification_token(app, jwt_config: JWTConfig):
    """Fixture to generate a sample email verification token for testing."""
    async with app.app_context():
        verification_url = generate_email_verification_token(
            "test@inspection.gc.ca", "https://www.example.com/", jwt_config
        )
    return verification_url
