"""
Login API Test
"""
import os
import pytest
from flask import Flask
from flask.testing import FlaskClient
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

@pytest.mark.usefixtures("set_allowed_domains")
def test_valid_login(login_url, test_client: FlaskClient):
    """Test case for valid login."""
    response = test_client.post(
        login_url,
        json={
            "email": "valid.email@inspection.gc.ca",
            "redirect_url": "http://localhost:3000/"
        }
    )
    assert response.status_code == 200

    allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
    print(allowed_domains)
    assert response.status_code == 200

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_email_format(login_url, test_client: FlaskClient):
    """Test case for invalid email format."""
    response = test_client.post(
        login_url,
        json={
            "email": "invalid.email",
            "redirect_url": "http://localhost:3000/"
        }
    )
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_email_not_provided(login_url, test_client: FlaskClient):
    """Test case for not provided email."""
    response = test_client.post(
        login_url,
        json={
            "redirect_url": "http://localhost:3000/"
        }
    )
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_redirect_url(login_url, test_client: FlaskClient):
    """Test case for invalid redirect url."""
    response = test_client.post(
        login_url,
        json={
            "email": "valid.email@example.com",
            "redirect_url": "htp:/localhost"
        }
    )
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_empty_json(login_url, test_client: FlaskClient):
    """Test case for empty json body."""
    response = test_client.post(
        login_url,
        json={}
    )
    assert response.status_code == 400
