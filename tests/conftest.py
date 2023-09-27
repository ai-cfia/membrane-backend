"""
Pytest configuration and shared fixtures for test setup.
"""
import logging
import unittest
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import jwt
from dotenv import load_dotenv

load_dotenv(".env.tests")

with patch("app_create.EmailClient.from_connection_string") as mock:
    mock.return_value = None
    from app import app

from emails import EmailConfig  # noqa: E402
from jwt_utils import JWTConfig, generate_email_verification_token  # noqa: E402


class TestConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client_private_key = cls.read_client_private_key()
        cls.jwt_config = cls.setup_jwt_config()
        cls.email_config = cls.setup_email_config()

    @classmethod
    def read_client_private_key(cls):
        with open("tests/client_private_keys/testapp1_private_key.pem", "rb") as f:
            return f.read()

    @classmethod
    def setup_jwt_config(cls):
        return JWTConfig(
            client_public_keys_folder=Path("tests/client_public_keys"),
            server_public_key=Path("tests/server_public_key/server_public_key.pem"),
            server_private_key=Path("tests/server_private_key/server_private_key.pem"),
            app_id_field="app_id",
            redirect_url_field="redirect_url",
            algorithm="RS256",
            data_field="data",
            jwt_access_token_expire_seconds=300,
            jwt_expire_seconds=300,
            token_blacklist=set(),
        )

    @classmethod
    def setup_email_config(cls):
        return EmailConfig(
            email_client=None,
            sender_email="",
            subject="Please Verify You Email Address",
            validation_pattern="^[a-zA-Z0-9._+]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$",
            email_send_success="Valid email address, Email sent with JWT link",
            html_content="<html><h1>{}</h1></html>",
            poller_wait_seconds=2,
            timeout=20,
        )

    def setUp(self):
        self.setup_app()
        self.test_client = self.app.test_client()
        self.setup_payload()

        # Suppress print statements
        self.held_output = StringIO()
        self.patcher = patch("sys.stdout", self.held_output)
        self.patcher.start()
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        pass

    def setup_app(self):
        self.app.config["JWT_CONFIG"] = self.jwt_config
        self.app.config["EMAIL_CONFIG"] = self.email_config
        self.app.config["TESTING"] = True
        self.app.config["SERVER_NAME"] = "login.example.com"

    def setup_payload(self):
        self.payload = {
            self.jwt_config.data_field: "test_data",
            self.jwt_config.app_id_field: "testapp1",
            self.jwt_config.redirect_url_field: "www.example.com",
        }

    def generate_jwt_token(self, payload, jwt_config: JWTConfig, app_id):
        if "exp" not in payload:
            expiration_seconds = datetime.utcnow() + timedelta(seconds=5 * 60)
            payload["exp"] = int(expiration_seconds.timestamp())
        headers = {
            "alg": jwt_config.algorithm,
            "typ": jwt_config.token_type,
            jwt_config.app_id_field: app_id,
        }
        return jwt.encode(
            payload, self.client_private_key, jwt_config.algorithm, headers
        )

    async def sample_verification_token(self):
        async with self.app.app_context():
            verification_url = generate_email_verification_token(
                "test@inspection.gc.ca", "https://www.example.com/", self.jwt_config
            )
        return verification_url
