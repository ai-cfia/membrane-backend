"""
Pytest configuration and shared fixtures for test setup.
"""
from pathlib import Path
import pytest
from flask import Flask
from jwt_utils import generate_email_verification_token
from generate_jwt import generate_jwt

# Import the Flask application instance from your app module
from app import app as flask_app

SERVER_PRIVATE_KEY = Path('tests/server_private_key/server_private_key.pem')

@pytest.fixture(scope='session')
def test_private_key():
    """Fixture to read and provide the private key."""
    with open('tests/client_private_keys/testapp1_private_key.pem', 'rb') as f:
        return f.read()

@pytest.fixture
def app():
    """Flask application fixture for the tests."""
    flask_app.config['SESSION_TYPE'] = 'memory'
    flask_app.config['TESTING'] = True
    # Add this configuration for SERVER_NAME
    flask_app.config['SERVER_NAME'] = 'localhost:5000'

    yield flask_app
    # pylint: disable=redefined-outer-name

@pytest.fixture
def test_client(app: Flask):
    """Test client fixture for the tests."""
    return app.test_client()

@pytest.fixture
def base_url():
    """Base URL fixture for the tests."""
    return '/'

@pytest.fixture
def login_url(base_url):
    """Login URL fixture for the tests."""
    return f'{base_url}authenticate'

@pytest.fixture
def set_allowed_domains(monkeypatch):  # noqa
    """Fixture to set the allowed email domains environment variable."""
    monkeypatch.setenv('ALLOWED_EMAIL_DOMAINS', 'gc.ca,canada.ca,inspection.gc.ca')

@pytest.fixture
def sample_jwt_token(generate_jwt_token):
    """Fixture to generate a sample JWT token for testing."""
    return generate_jwt_token({
        "data": "test_data",
        "app_id": "testapp1",
        "redirect_url": "https://www.example.com"
    })

@pytest.fixture
def generate_jwt_token(test_private_key):
    """Fixture to generate JWT tokens for testing purposes."""
    def _generator(payload, headers=None):
        return generate_jwt(payload, test_private_key, headers=headers)

    return _generator

@pytest.fixture
def sample_verification_token(app):
    """Fixture to generate a sample email verification token for testing."""
    with app.app_context():
        print(SERVER_PRIVATE_KEY)
        verification_url = generate_email_verification_token(
            'test@inspection.gc.ca',
            'https://www.example.com/',
            int(30),
            SERVER_PRIVATE_KEY
        )
    return verification_url
