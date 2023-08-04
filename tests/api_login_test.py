"""
Login API Test
"""
import os
from pathlib import Path  # Python 3.6+ only
import pytest
from flask import Flask
from flask.testing import FlaskClient
from dotenv import load_dotenv

# Import the Flask application instance from your app module
from app import app as flask_app

env_path = Path('../') / '.env'
load_dotenv(dotenv_path=env_path)

print(os.environ)

@pytest.fixture
def app():
    """Flask application fixture for the tests."""
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

def test_valid_login(login_url, test_client: FlaskClient):
    """Test case for valid login."""
    os.environ['ALLOWED_EMAIL_DOMAINS'] = os.getenv('ALLOWED_EMAIL_DOMAINS')
    response = test_client.post(
        login_url,
        json={
            "email": "valid.email@inspection.gc.ca",
            "redirect_url": "http://localhost:3000/"
        }
    )

    allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
    print(allowed_domains)
    assert response.status_code == 200

def test_invalid_email_format(login_url, test_client: FlaskClient):
    """Test case for invalid email format."""
    os.environ['ALLOWED_EMAIL_DOMAINS'] = os.getenv('ALLOWED_EMAIL_DOMAINS')
    response = test_client.post(
        login_url,
        json={
            "email": "invalid.email",
            "redirect_url": "http://localhost:3000/"
        }
    )
    assert response.status_code == 400

def test_email_not_provided(login_url, test_client: FlaskClient):
    """Test case for not provided email."""
    os.environ['ALLOWED_EMAIL_DOMAINS'] = os.getenv('ALLOWED_EMAIL_DOMAINS')
    response = test_client.post(
        login_url,
        json={
            "redirect_url": "http://localhost:3000/"
        }
    )
    assert response.status_code == 400

def test_invalid_redirect_url(login_url, test_client: FlaskClient):
    """Test case for invalid redirect url."""
    os.environ['ALLOWED_EMAIL_DOMAINS'] = os.getenv('ALLOWED_EMAIL_DOMAINS')
    response = test_client.post(
        login_url,
        json={
            "email": "valid.email@example.com",
            "redirect_url": "htp:/localhost"
        }
    )
    assert response.status_code == 400

def test_empty_json(login_url, test_client: FlaskClient):
    """Test case for empty json body."""
    os.environ['ALLOWED_EMAIL_DOMAINS'] = os.getenv('ALLOWED_EMAIL_DOMAINS')
    response = test_client.post(
        login_url,
        json={}
    )
    assert response.status_code == 400
