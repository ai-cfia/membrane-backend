"""
Verify Token Test Cases.
"""
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from quart.testing import QuartClient

from jwt_utils import JWTConfig


@pytest.mark.asyncio
async def test_missing_token_returns_405_method_not_allowed(test_client: QuartClient):
    """Test case for missing token."""
    response = await test_client.get("/authenticate")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_invalid_token_returns_422_unprocessable_content(
    test_client: QuartClient,
):
    """Test case for invalid token provided."""
    response = await test_client.get("/authenticate?token=invalid_token_here")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_client_jwt_without_email_returns_302_found(
    test_client: QuartClient, sample_jwt_token
):
    """
    Test the scenario where the request only contains a valid client JWT without an
    email
    """
    response = await test_client.get(f"/authenticate?token={sample_jwt_token}")
    # Assertions to check the desired behavior.
    # If the request only contains a valid client JWT without an email, ...
    # ... then the user gets redirected to Membrane Frontend.
    assert response.status_code == 302


@pytest.mark.asyncio
@patch("app.app.add_background_task")
async def test_email_provided_returns_200_ok(
    mock_add_background_task,
    test_client: QuartClient,
    sample_jwt_token,
):
    mock_add_background_task.return_value = None
    """
    Test the scenario where the request contains both a valid client JWT and an email
    """
    response = await test_client.get(
        f"/authenticate?token={sample_jwt_token}",
        json={"email": "test@inspection.gc.ca"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_email_provided_returns_405_method_not_allowed(
    test_client: QuartClient, sample_jwt_token
):
    """
    Test the scenario where the request contains both a valid client JWT and an invalid
    email
    """
    response = await test_client.get(
        f"/authenticate?token={sample_jwt_token}",
        json={"email": "test@inspection.g.ca"},
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_extract_with_expired_jwt_returns_405_method_not_allowed(
    test_client: QuartClient, generate_jwt_token, payload: dict, jwt_config: JWTConfig
):
    """Test case for expired JWT token."""
    # Set the expiration timestamp to 2 days ago
    expired_timestamp = int((datetime.utcnow() - timedelta(days=2)).timestamp())
    payload.update({jwt_config.expiration_field: expired_timestamp})
    expired_token = generate_jwt_token(payload, jwt_config, "testapp1")
    response = await test_client.get(f"/authenticate?token={expired_token}")
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_valid_verification_token_returns_302_found(
    test_client: QuartClient, sample_verification_token
):
    """
    Test the scenario where the request only contains a valid client JWT without an
    email
    """
    response = await test_client.get(await sample_verification_token)
    # If the request contains a valid email verification token, ...
    # ... then redirect the user to client application.
    assert response.status_code == 302


@pytest.mark.asyncio
async def test_invalid_verification_token_returns_405_method_not_allowed(
    test_client: QuartClient, sample_verification_token
):
    """Test the scenario where the request only contains an invalid client JWT"""
    response = await test_client.get(await sample_verification_token + "invalid_string")
    # If the request contains an invalid email verification token, then throw error.
    assert response.status_code == 405
