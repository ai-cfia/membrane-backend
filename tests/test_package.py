import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import asymmetric, serialization
from flask import Flask

from membrane.client import (
    Certificate,
    User,
    blueprint,
    configure,
    create_custom_token,
    login_user,
    logout_user,
    verify_token,
)


class TestMembranePackage(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = "test_secret_key"
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        private_key = asymmetric.rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        self.app_id = "test_app_id"
        self.auth_url = "test_auth_uri"
        self.certificate_data = {
            "app_id": self.app_id,
            "server_public_key": public_pem,
            "client_private_key": private_pem,
            "auth_url": self.auth_url,
        }
        self.test_token_expiration = 300
        self.test_custom_claims = {"foo": "bar"}

        configure(
            self.app,
            self.certificate_data,
            self.test_token_expiration,
            self.test_custom_claims,
        )
        self.app.register_blueprint(blueprint)

    def test_create_verify_valid_jwt(self):
        headers = {"alg": "RS256", "app_id": "test_app_id", "typ": "JWT"}
        expiration = datetime.utcnow() + timedelta(seconds=self.test_token_expiration)
        timestamp = int(expiration.timestamp())
        redirect_url = "https://redirect.here"

        token = create_custom_token(redirect_url)
        unverified_header = jwt.get_unverified_header(token)
        self.assertDictEqual(unverified_header, headers)

        decoded_data = verify_token(token)
        self.assertEqual(decoded_data["foo"], "bar")
        self.assertEqual(decoded_data["app_id"], self.app_id)
        self.assertEqual(decoded_data["redirect_url"], redirect_url)
        self.assertLessEqual(decoded_data["exp"], timestamp + 1)

    # TODO: test create and verify token failures


if __name__ == "__main__":
    unittest.main()
