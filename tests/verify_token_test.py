"""
Verify Token Test Cases.
"""
from flask.testing import FlaskClient
import pytest

# Constants
SECRET_KEY = 'super-secret'
ALGORITHM = 'HS256'

@pytest.mark.usefixtures("set_allowed_domains")
def test_missing_token(test_client: FlaskClient):
    """Test case for missing token."""
    response = test_client.get("/authenticate")
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_invalid_token(test_client: FlaskClient):
    """Test case for invalid token."""
    response = test_client.get("/authenticate?token=invalidtokenhere")
    print(response.data)  # This prints the actual response data during the test.
    assert response.status_code == 400

@pytest.mark.usefixtures("set_allowed_domains")
def test_authenticate_no_stage(test_client: FlaskClient, sample_jwt_token):
    """Test the scenario where the 'stage' is not set in the session."""
    response = test_client.get(f"/authenticate?token={sample_jwt_token}")
    print(response)
    # Assertions to check the desired behavior.
    assert response.status_code == 302

@pytest.mark.usefixtures("set_allowed_domains")
def test_authenticate_JWT_Missing_stage(test_client: FlaskClient, sample_jwt_token):
    """Test the scenario where the 'stage' is not set in the session."""
    response = test_client.get(f"/authenticate?token={sample_jwt_token}",
                               json={"email": "test@inspection.gc.ca"})
    print(response)
    # Assertions to check the desired behavior.
    assert response.status_code == 302

"""
@pytest.mark.usefixtures("set_allowed_domains")
def test_authenticate_with_stage(test_client: FlaskClient, sample_jwt_token):
    
    Test the scenario where the 'stage' is set as 'email_sent' in the session, 
    simulating the user clicking on the verification email link.
    
    # Step 1: Simulate the first request
    response = test_client.get(f"/authenticate?token={sample_jwt_token}",
                               json={"email": "test@inspection.gc.ca"})
    assert response.status_code == 200

    # Step 2: 'stage' should be set as 'email_sent' in the session. Simulate the second request by using the same JWT token
    second_response = test_client.get(f"/authenticate?token={sample_jwt_token}")

    # Assertions to check the desired behavior for the second request
    assert second_response.status_code == 302
    assert second_response.headers['Location'] == "https://www.example.com"

@pytest.mark.usefixtures("set_allowed_domains")
def test_authenticate_with_blacklisted_token(test_client: FlaskClient, sample_jwt_token):
    Test the scenario where a token has already been used and added to the blacklist.
    # Step 1: Simulate the first request as you did in the previous test
    response = test_client.get(f"/authenticate?token={sample_jwt_token}",
                               json={"email": "test@inspection.gc.ca"})
    assert response.status_code == 200

    # Step 2: Simulate the second request by using the same JWT token, this simulates user clicking the email link.
    second_response = test_client.get(f"/authenticate?token={sample_jwt_token}")
    assert second_response.status_code == 302
    assert second_response.headers['Location'] == "https://www.example.com"

    # Step 3: Now, try to use the JWT token a third time. Since the token should be blacklisted after the second request, this should result in an error.
    third_response = test_client.get(f"/authenticate?token={sample_jwt_token}")
    assert third_response.status_code == 400  # Assuming 400 as the status code for a blacklisted token based on your previous code
    response_data = third_response.get_json()
    assert response_data['error'] == "This token has already been used."

    """