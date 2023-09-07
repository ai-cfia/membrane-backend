"""
Verify Token Test Cases.
"""
from datetime import timedelta, datetime
from flask.testing import FlaskClient
import pytest

# Constants
SECRET_KEY = 'super-secret'
ALGORITHM = 'HS256'

@pytest.mark.usefixtures("set_allowed_domains")
def test_missing_token(test_client: FlaskClient):
    """Test case for missing token."""
    response = test_client.get("/authenticate")
    assert response.status_code == 405

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_token(test_client: FlaskClient):
    """Test case for invalid token provided."""
    response = test_client.get("/authenticate?token=invalidtokenhere")
    print(response.data)  # This prints the actual response data during the test.
    assert response.status_code == 422

@pytest.mark.usefixtures("set_allowed_domains")
def test_authenticate_no_stage(test_client: FlaskClient, sample_jwt_token):
    """Test the scenario where the request only contains a valid client JWT without an email"""
    response = test_client.get(f"/authenticate?token={sample_jwt_token}")
    print(response)
    # Assertions to check the desired behavior.
    assert response.status_code == 302

@pytest.mark.usefixtures("set_allowed_domains")
def test_email_provided(test_client: FlaskClient, sample_jwt_token):
    """Test the scenario where the request contains both a valid client JWT and an email"""
    response = test_client.get(f"/authenticate?token={sample_jwt_token}",
                               json={"email": "test@inspection.gc.ca"})
    print(response)
    # Assertions to check the desired behavior.
    assert response.status_code == 200

@pytest.mark.usefixtures("set_allowed_domains")
def test_extract_with_expired_jwt(test_client: FlaskClient, generate_jwt_token):
    """Test case for expired JWT token."""

    # Set the expiration timestamp to 2 days ago
    expired_timestamp = int((datetime.utcnow() - timedelta(days=2)).timestamp())

    # Generate an expired JWT token
    expired_token = generate_jwt_token({
        "data": "test_data",
        "app_id": "testapp1",
        "redirect_url": "https://www.example.com",
        "exp": expired_timestamp
    })

    print(f"Expired Token Timestamp: {expired_timestamp}")
    print(f"Current Timestamp: {int(datetime.utcnow().timestamp())}")

    # Make a request with the expired token
    response = test_client.get(f"/authenticate?token={expired_token}")

    # Expect a 400 status code, as the token is expired
    assert response.status_code == 405
