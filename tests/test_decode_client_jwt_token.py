"""
Tests for JWT Token Decoding Operations.
"""
import unittest

from conftest import TestConfig

from jwt_utils import JWTError, JWTPublicKeyNotFoundError, decode_client_jwt_token


class TestJWTDecoding(TestConfig, unittest.TestCase):
    def test_decode_jwt_without_app_id(self):
        payload = {self.jwt_config.data_field: "test_data"}
        jwt_token = self.generate_jwt_token(payload, self.jwt_config, "testapp1")
        with self.assertRaisesRegex(JWTError, "No app id in JWT payload."):
            decode_client_jwt_token(jwt_token, self.jwt_config)

    def test_decode_jwt_with_nonexistent_app_id(self):
        self.payload.update({self.jwt_config.app_id_field: "nonexistent"})
        jwt_token = self.generate_jwt_token(self.payload, self.jwt_config, "testapp1")
        with self.assertRaises(JWTPublicKeyNotFoundError):
            decode_client_jwt_token(jwt_token, self.jwt_config)

    def test_decode_jwt_with_invalid_token(self):
        invalid_jwt = "invalid.jwt.token"
        with self.assertRaises(Exception):
            decode_client_jwt_token(invalid_jwt, self.jwt_config)

    def test_decode_jwt_invalid_signature(self):
        jwt_token = self.generate_jwt_token(self.payload, self.jwt_config, "testapp1")
        jwt_token = jwt_token[:-3] + "abc"
        with self.assertRaises(JWTError):
            decode_client_jwt_token(jwt_token, self.jwt_config)

    def test_decode_jwt_malformed_header(self):
        jwt_token = self.generate_jwt_token(self.payload, self.jwt_config, "testapp1")
        jwt_parts = jwt_token.split(".")
        jwt_parts[0] = jwt_parts[0] + "malformed"
        jwt_token = ".".join(jwt_parts)
        with self.assertRaises(Exception):
            decode_client_jwt_token(jwt_token, self.jwt_config)
