import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt

from app_creator import create_app
from config import AppConfig, EmailConfig, JWTConfig
from tests.test_helpers import generate_key_pair


def generate_client_keys(client_id, private_key_suffix, public_key_suffix):
    """Generate a pair of keys for a client app."""
    private, public = generate_key_pair()
    keys = {
        f"{client_id}{private_key_suffix}": private,
        f"{client_id}{public_key_suffix}": public,
    }
    return keys


class TestEmailConfig(EmailConfig):
    """Email config for testing purposes."""
    email_client = None
    sender_email = "sender"


class TestJWTConfig(JWTConfig):
    """JWT config for testing purposes."""
    token_blacklist = set()
    server_private_key, server_public_key = generate_key_pair()
    client_keys = generate_client_keys("test-app", "private", "public")
    private_key_suffix = "private"
    public_key_suffix = "public"
    algorithm = "RS256"
    token_type = "JWT"


class TestAppConfig(AppConfig):
    """App config for testing purposes."""
    CORS_ALLOWED_ORIGINS = []
    MEMBRANE_FRONTEND = "frontend"
    SECRET_KEY = "secret"
    JWT_CONFIG = TestJWTConfig()
    EMAIL_CONFIG = TestEmailConfig()
    SESSION_TYPE = "filesystem"
    LOGGING_LEVEL = "CRITICAL"


def generate_client_token(payload, jwt_config: TestJWTConfig, app_id):
    """Generate client JWT token."""
    if "exp" not in payload:
        expiration_seconds = datetime.utcnow() + timedelta(seconds=5 * 60)
        payload["exp"] = int(expiration_seconds.timestamp())
    headers = {
        "alg": jwt_config.algorithm,
        "typ": jwt_config.token_type,
        "app_id": app_id,
    }
    private_key_id = f"{app_id}{jwt_config.private_key_suffix}"
    return jwt.encode(
        payload, jwt_config.client_keys[private_key_id], jwt_config.algorithm, headers
    )


def generate_server_token(payload, jwt_config: TestJWTConfig):
    """Generate server JWT token."""
    if "exp" not in payload:
        expiration_time = datetime.utcnow() + timedelta(
            seconds=jwt_config.jwt_expire_seconds
        )
        expiration_timestamp = int(expiration_time.timestamp())
        payload.update({"exp": expiration_timestamp})
    return jwt.encode(payload, jwt_config.server_private_key, jwt_config.algorithm)


class TestRoutes(unittest.TestCase):
    """Test case for application routes."""

    def setUp(self):
        self.config = TestAppConfig()
        self.app = create_app(self.config)
        self.test_client = self.app.test_client()
        self.client_payload = {
            "data": "test_data",
            "app_id": "test-app",
            "redirect_url": "www.example.com",
        }
        self.server_payload = {
            "sub": "email@example.com",
            "redirect_url": "redirect_url",
        }

    @patch("routes.send_email")
    def test_login_valid_email_valid_token(self, mock_send_email):
        """Test login with valid email and valid token."""
        mock_send_email.return_value = None
        sample_jwt_token = generate_client_token(
            self.client_payload, self.config.JWT_CONFIG, "test-app"
        )
        response = self.test_client.post(
            f"/login?token={sample_jwt_token}",
            json={"email": "test@inspection.gc.ca"},
        )
        self.assertEqual(response.status_code, 200)

    def test_login_missing_token(self):
        """Test login with missing token."""
        response = self.test_client.post("/login")
        self.assertEqual(response.status_code, 400)

    def test_login_valid_email_invalid_token(self):
        """Test login with valid email but invalid token."""
        response = self.test_client.post(
            "/login?token=invalid_token_here",
            json={"email": "test@inspection.gc.ca"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_valid_token_invalid_email(self):
        """Test login with valid token but invalid email."""
        sample_jwt_token = generate_client_token(
            self.client_payload, self.config.JWT_CONFIG, "test-app"
        )
        response = self.test_client.post(
            f"/login?token={sample_jwt_token}",
            json={"email": "test@inspection.g.ca"},
        )
        self.assertEqual(response.status_code, 400)

    def test_authenticate_valid_token(self):
        """Test authenticate with valid token."""
        sample_jwt_token = generate_client_token(
            self.client_payload, self.config.JWT_CONFIG, "test-app"
        )
        response = self.test_client.get(f"/authenticate?token={sample_jwt_token}")
        self.assertEqual(response.status_code, 302)

    def test_authenticate_missing_token(self):
        """Test authenticate with missing token."""
        response = self.test_client.get("/authenticate")
        self.assertEqual(response.status_code, 400)

    def test_authenticate_invalid_token(self):
        """Test authenticate with invalid token."""
        response = self.test_client.get("/authenticate?token=invalid_token")
        self.assertEqual(response.status_code, 401)

    def test_authenticate_expired_token(self):
        """Test authenticate with expired token."""
        expired_timestamp = int((datetime.utcnow() - timedelta(days=2)).timestamp())
        self.client_payload.update({"exp": expired_timestamp})
        expired_token = generate_client_token(
            self.client_payload, self.config.JWT_CONFIG, "test-app"
        )
        response = self.test_client.get(f"/authenticate?token={expired_token}")
        self.assertEqual(response.status_code, 401)

    def test_verify_email_valid_token(self):
        """Test verify email with valid token."""
        sample_jwt_token = generate_server_token(
            self.server_payload, self.config.JWT_CONFIG
        )
        response = self.test_client.get(f"/verify_email?token={sample_jwt_token}")
        self.assertEqual(response.status_code, 302)

    def test_verify_email_no_token(self):
        """Test verify email with no token."""
        response = self.test_client.get("/verify_email")
        self.assertEqual(response.status_code, 400)

    def test_verify_email_invalid_token(self):
        """Test verify email with invalid token."""
        response = self.test_client.get("/verify_email?token=invalid_token")
        self.assertEqual(response.status_code, 401)

    def test_verify_email_expired_token(self):
        """Test verify email with expired token."""
        expired_timestamp = int((datetime.utcnow() - timedelta(days=2)).timestamp())
        self.server_payload.update({"exp": expired_timestamp})
        expired_token = generate_server_token(
            self.server_payload, self.config.JWT_CONFIG
        )
        response = self.test_client.get(f"/verify_email?token={expired_token}")
        self.assertEqual(response.status_code, 401)
