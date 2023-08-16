"""
Login API Test
"""
import os
import pytest
from flask.testing import FlaskClient
from generate_jwt import generate_jwt

TEST_PRIVATE_KEY = open('tests/test_private_keys/test1_private_key.pem', 'rb').read()

def generate_valid_jwt():
    """Generate a valid JWT token with the required app_id"""
    jwt_data = {
        "app_id": "app1",
        "redirect_url": "https://www.google.com/"
    }
    return generate_jwt(jwt_data, TEST_PRIVATE_KEY)

@pytest.mark.usefixtures("set_allowed_domains")
def test_valid_login(login_url, test_client: FlaskClient):
    """Test case for valid login."""

    jwt_token = generate_valid_jwt()
    response = test_client.post(
        f"{login_url}?token={jwt_token}",
        json={
            "email": "valid.email@inspection.gc.ca",
        }
    )
    
    allowed_domains = os.getenv('ALLOWED_EMAIL_DOMAINS', '')
    print(allowed_domains)
    assert response.status_code == 200

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_email_format(login_url, test_client: FlaskClient):
    """Test case for invalid email format."""

    jwt_token = generate_valid_jwt()
    response = test_client.post(
        f"{login_url}?token={jwt_token}",
        json={
            "email": "invalid.email",
        }
    )
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_email_not_provided(login_url, test_client: FlaskClient):
    """Test case for not provided email."""

    jwt_token = generate_valid_jwt()
    response = test_client.post(
        f"{login_url}?token={jwt_token}",
        json={
        }
    )
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_redirect_url(login_url, test_client: FlaskClient):
    """Test case for invalid redirect url."""

    jwt_token = generate_valid_jwt()
    response = test_client.post(
        f"{login_url}?token={jwt_token}",
        json={
            "email": "valid.email@example.com",
        }
    )
    assert response.status_code == 400
