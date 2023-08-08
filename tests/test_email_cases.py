"""
Email Test Cases
"""
import uuid
import pytest
from flask.testing import FlaskClient

emails_to_test = [
    # Valid email cases
    *[(f"valid.{uuid.uuid4()}@inspection.gc.ca", True) for _ in range(50)],
    # Invalid email cases
    *[(f"invalid.{uuid.uuid4()}@randomsite.com", False) for _ in range(50)]
]

@pytest.mark.usefixtures("set_allowed_domains")
@pytest.mark.parametrize("email, expected_success", emails_to_test)
def test_email_cases(test_client: FlaskClient, login_url, email, expected_success):
    """Test case for different email cases."""
    response = test_client.post(
        login_url,
        json={
            "email": email,
            "redirect_url": "http://localhost:3000/"
        }
    )

    if expected_success:
        assert response.status_code == 200
    else:
        assert response.status_code == 400
