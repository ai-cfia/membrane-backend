import os
import uuid
from datetime import timedelta
from dotenv import load_dotenv

import jwt
from quart import Quart, redirect, request, session, url_for

from generate_jwt import generate_jwt

load_dotenv(".env.tests")

app = Quart(__name__)

# Generate a secret key for the session cookie
SECRET_KEY = os.getenv("MEMBRANE_SECRET_KEY", str(uuid.uuid4()))
app.secret_key = SECRET_KEY

session_lifetime_seconds = int(os.getenv("MEMBRANE_SESSION_LIFETIME_SECONDS", 30))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=session_lifetime_seconds)


def decode_jwt_token(jwt_token, public_key):
    """
    Decoding the JWT using the given public key.
    """
    try:
        algorithm = os.getenv("MEMBRANE_ENCODE_ALGORITHM")
        decoded_token = jwt.decode(jwt_token, public_key, algorithms=[algorithm])
        return decoded_token
    except Exception as error:
        print(f"Error decoding JWT: {error}")
        return None


@app.route("/health")
async def health():
    return os.getenv("MEMBRANE_HEALTH_MESSAGE"), 200


@app.route("/")
async def hello_world():
    # Check if there's a session cookie
    if "authenticated" in session and session["authenticated"]:
        email = session["decoded_token"]["sub"]  # Get the email from the decoded token
        return f"Hello, {email}!"

    # Check if there's a JWT token in the request from another backend
    jwt_token = request.args.get("token")
    if not jwt_token:
        # Generate JWT token
        with open(os.getenv("MEMBRANE_TEST_APP_PRIVATE_KEY", ""), "rb") as file:
            private_key_content = file.read()

        app_id_field = os.getenv("MEMBRANE_APP_ID_FIELD")
        app_id = os.getenv("MEMBRANE_APP_ID")
        redirect_url_field = os.getenv("MEMBRANE_REDIRECT_URL_FIELD")
        algorithm = os.getenv("MEMBRANE_ENCODE_ALGORITHM")
        type = os.getenv("MEMBRANE_TOKEN_TYPE")
        data = {
            app_id_field: app_id,
            redirect_url_field: url_for("hello_world", _external=True),
        }
        jwt_token = generate_jwt(
            data,
            private_key_content,
            {"alg": algorithm, "typ": type, app_id_field: app_id},
        )
        # Redirect to /authenticate with the generated JWT token
        print("Generate JWT token AND SENT OUT")
        return redirect(f"http://127.0.0.1:5000/authenticate?token={jwt_token}")

    # If there is a JWT token, validate and decode it
    with open(os.getenv("MEMBRANE_SERVER_PUBLIC_KEY"), "rb") as file:
        public_key_content = file.read()

    decoded_token = decode_jwt_token(jwt_token, public_key_content)

    if decoded_token:
        # If the JWT token is valid, generate a session cookie
        print("JWT token VALID")
        session.permanent = True
        session["authenticated"] = True
        session[
            "decoded_token"
        ] = decoded_token  # Store the decoded token in the session
        return redirect(url_for("hello_world"))

    return "Invalid Token!"


if __name__ == "__main__":
    app.run(debug=True)
