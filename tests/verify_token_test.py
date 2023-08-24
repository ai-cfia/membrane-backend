"""
Verify Token Test Cases.
"""
import time
from pathlib import Path
from datetime import timedelta, datetime
from flask import Flask
from flask.testing import FlaskClient
import pytest
from jwt_utils import encode_jwt_token

# Constants
SECRET_KEY = 'super-secret'
ALGORITHM = 'HS256'

@pytest.mark.usefixtures("set_allowed_domains")
def test_missing_token(test_client: FlaskClient):
    """Test case for missing token."""
    response = test_client.get("/verify_token")
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_token(test_client: FlaskClient):
    """Test case for invalid token."""
    response = test_client.get("/verify_token?token=invalidtokenhere")
    print(response.data)  # This prints the actual response data during the test.
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_valid_token(test_client: FlaskClient, app: Flask):
    """Test case for valid token."""

    # Using the Flask application context
    with app.app_context():
        # Mimic the /login payload
        email = "test.email@inspection.gc.ca"
        redirect_url = "https://www.google.com/"

        expiration_time = datetime.utcnow() + timedelta(minutes=15)
        expiration_timestamp = int(expiration_time.timestamp())
        payload = {
            "sub": email,
            "redirect_url": redirect_url,
            "app_id": "test2",
            "exp": expiration_timestamp
        }

        # Using the private key to encode the JWT token
        jwt_token = encode_jwt_token(payload, Path("tests/test_private_keys/test2_private_key.pem"))
    # Use the generated token to test the /verify_token endpoint
    response = test_client.get(f"/verify_token?token={jwt_token}")

    # Check for successful redirection
    assert response.status_code == 302
    # Optional: Check if redirection URL matches the provided redirect_url
    assert response.location == redirect_url

@pytest.mark.usefixtures("set_allowed_domains")
def test_blacklisted_token(test_client: FlaskClient, app: Flask):
    """Test case for blacklisted token."""

    # Using the Flask application context
    with app.app_context():
        # Mimic the /login payload
        email = "test.email@inspection.gc.ca"
        redirect_url = "https://www.google.com/"

        expiration_time = datetime.utcnow() + timedelta(minutes=2)
        expiration_timestamp = int(expiration_time.timestamp())
        payload = {
            "sub": email,
            "redirect_url": redirect_url,
            "app_id": "test2",
            "exp": expiration_timestamp
        }

        # Using the private key to encode the JWT token
        jwt_token = encode_jwt_token(payload, Path("tests/test_private_keys/test2_private_key.pem"))

    # Use the generated token to test the /verify_token endpoint the first time
    response_first = test_client.get(f"/verify_token?token={jwt_token}")

    # Check for successful redirection
    assert response_first.status_code == 302
    # Optional: Check if redirection URL matches the provided redirect_url
    assert response_first.location == redirect_url

    # Now, try to use the same token a second time
    response_second = test_client.get(f"/verify_token?token={jwt_token}")

    # Check that the response is an error due to the token being blacklisted
    assert response_second.status_code == 400
