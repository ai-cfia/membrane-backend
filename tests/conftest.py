"""
Pytest configuration and shared fixtures for test setup.
"""
import pytest
from flask import Flask
from generate_jwt import generate_jwt

# Import the Flask application instance from your app module
from app import app as flask_app

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
