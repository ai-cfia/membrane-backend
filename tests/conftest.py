import pytest
from flask import Flask
from flask_session import Session

# Import the Flask application instance from your app module
from app import app as flask_app

@pytest.fixture
def app():
    """Flask application fixture for the tests."""
    flask_app.config['SESSION_TYPE'] = 'memory'
    flask_app.config['SESSION_PERMANENT'] = False

    session = Session()
    session.init_app(flask_app)

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
    return f'{base_url}login'

@pytest.fixture
def set_allowed_domains(monkeypatch):  # noqa
    """Fixture to set the allowed email domains environment variable."""
    monkeypatch.setenv('ALLOWED_EMAIL_DOMAINS', 'gc.ca,canada.ca,inspection.gc.ca')
