# """
# Verify Token Test Cases.
# """
from datetime import datetime, timedelta
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from conftest import TestConfig


class TestAuthenticationFlow(TestConfig, IsolatedAsyncioTestCase):
    async def test_missing_token_returns_405_method_not_allowed(self):
        response = await self.test_client.get("/authenticate")
        self.assertEqual(response.status_code, 405)

    async def test_invalid_token_returns_422_unprocessable_content(self):
        response = await self.test_client.get("/authenticate?token=invalid_token_here")
        self.assertEqual(response.status_code, 405)

    async def test_client_jwt_without_email_returns_302_found(self):
        sample_jwt_token = self.generate_jwt_token(
            self.payload, self.jwt_config, "testapp1"
        )
        response = await self.test_client.get(f"/authenticate?token={sample_jwt_token}")
        self.assertEqual(response.status_code, 302)

    @patch("app.app.add_background_task")
    async def test_email_provided_returns_200_ok(self, mock_add_background_task):
        mock_add_background_task.return_value = None
        sample_jwt_token = self.generate_jwt_token(
            self.payload, self.jwt_config, "testapp1"
        )
        response = await self.test_client.get(
            f"/authenticate?token={sample_jwt_token}",
            json={"email": "test@inspection.gc.ca"},
        )
        self.assertEqual(response.status_code, 200)

    async def test_invalid_email_provided_returns_405_method_not_allowed(self):
        sample_jwt_token = self.generate_jwt_token(
            self.payload, self.jwt_config, "testapp1"
        )
        response = await self.test_client.get(
            f"/authenticate?token={sample_jwt_token}",
            json={"email": "test@inspection.g.ca"},
        )
        self.assertEqual(response.status_code, 405)

    async def test_extract_with_expired_jwt_returns_405_method_not_allowed(self):
        expired_timestamp = int((datetime.utcnow() - timedelta(days=2)).timestamp())
        self.payload.update({"exp": expired_timestamp})
        expired_token = self.generate_jwt_token(
            self.payload, self.jwt_config, "testapp1"
        )
        response = await self.test_client.get(f"/authenticate?token={expired_token}")
        self.assertEqual(response.status_code, 405)

    async def test_valid_verification_token_returns_302_found(self):
        sample_verification_token = await self.sample_verification_token()
        response = await self.test_client.get(sample_verification_token)
        self.assertEqual(response.status_code, 302)

    async def test_invalid_verification_token_returns_405_method_not_allowed(self):
        sample_verification_token = await self.sample_verification_token()
        response = await self.test_client.get(
            sample_verification_token + "invalid_string"
        )
        self.assertEqual(response.status_code, 405)
