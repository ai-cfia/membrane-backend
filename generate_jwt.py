"""
Utility script to generate JWT tokens for testing and development.
"""
import os
from datetime import datetime, timedelta

import jwt


def generate_jwt(data, priv_key, headers=None):
    """
    Generate a JWT using the given data and private key.
    """
    app_id_field = os.getenv("MEMBRANE_APP_ID_FIELD")
    app_id = os.getenv("MEMBRANE_APP_ID")
    expiration_field = os.getenv("MEMBRANE_EXPIRATION_FIELD")
    algorithm = os.getenv("MEMBRANE_ENCODE_ALGORITHM")
    type = os.getenv("MEMBRANE_TOKEN_TYPE")

    # Set the expiration time for the JWT
    if expiration_field not in data:
        # Set the expiration time for the JWT
        expiration_time = datetime.utcnow() + timedelta(seconds=5 * 60)
        data[expiration_field] = int(expiration_time.timestamp())

    # Use the default header if none is provided
    if headers is None:
        headers = {"alg": algorithm, "typ": type, app_id_field: app_id}

    jwt_token = jwt.encode(data, priv_key, algorithm=algorithm, headers=headers)
    return jwt_token


if __name__ == "__main__":
    app_id_field = os.getenv("MEMBRANE_APP_ID_FIELD")
    app_id = os.getenv("MEMBRANE_APP_ID")
    redirect_url_field = os.getenv("MEMBRANE_REDIRECT_URL_FIELD")
    redirect_url = os.getenv("MEMBRANE_REDIRECT_URL")
    test_app_private_key = os.getenv("MEMBRANE_TEST_APP_PRIVATE_KEY", "")

    # Load the private key
    with open(test_app_private_key, "rb") as f:
        private_key_content = f.read()

    # Sample data with a redirect_url and app_id
    sample_data = {app_id_field: app_id, redirect_url_field: redirect_url}

    # Generate the JWT
    GENERATED_JWT = generate_jwt(sample_data, private_key_content)
    print(f"Generated JWT: {GENERATED_JWT}")
