"""
Verify Token Test Cases
"""
from flask import Flask
import pytest
from flask_jwt_extended import create_access_token
from flask.testing import FlaskClient

# Constants
SECRET_KEY = 'super-secret'
ALGORITHM = 'HS256'

@pytest.mark.usefixtures("set_allowed_domains")
def test_missing_token(test_client: FlaskClient):
    """Test case for missing token."""
    response = test_client.get("/verify_token")
    assert response.status_code == 400
    assert response.json == {"error": "No token provided."}


@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_token(test_client: FlaskClient):
    """Test case for invalid token."""
    response = test_client.get("/verify_token?token=invalidtokenhere")
    assert response.status_code == 400
    assert response.json == {"error": "Invalid token."}


@pytest.mark.usefixtures("set_allowed_domains")
def test_valid_token(test_client: FlaskClient, app: Flask):
    """Test case for valid token."""
    # Using the Flask application context
    with app.app_context():
        # Create a valid JWT token
        email = "test.email@inspection.gc.ca"
        redirect_url = "localhost:3000/"
        claims = {"redirect_url": redirect_url}
        token = create_access_token(identity=email, additional_claims=claims)

    response = test_client.get(f"/verify_token?token={token}")
    # Here we're just checking if the token is successfully verified.
    # You can extend this test to check for specific session data or response headers based on your logic.
    assert response.status_code == 302  # Assuming a successful token leads to a redirection
