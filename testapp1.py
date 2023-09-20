import os
import uuid
from datetime import timedelta

import jwt
from quart import Quart, redirect, request, session, url_for

from generate_jwt import generate_jwt

app = Quart(__name__)

# Generate a secret key for the session cookie
SECRET_KEY = os.getenv("SECRET_KEY", str(uuid.uuid4()))
app.secret_key = SECRET_KEY

session_lifetime_minutes = int(os.environ.get("SESSION_LIFETIME_MINUTES", 30))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=session_lifetime_minutes)


def decode_jwt_token(jwt_token, public_key):
    """
    Decoding the JWT using the given public key.
    """
    try:
        decoded_token = jwt.decode(jwt_token, public_key, algorithms=["RS256"])
        return decoded_token
    except Exception as error:
        print(f"Error decoding JWT: {error}")
        return None


@app.route("/health")
async def health_check():
    return "ok", 200


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
        with open("keys/testapp1_private_key.pem", "rb") as file:
            private_key_content = file.read()
        data = {
            "app_id": "testapp1",
            "redirect_url": url_for("hello_world", _external=True),
        }
        jwt_token = generate_jwt(data, private_key_content)
        # Redirect to /authenticate with the generated JWT token
        print("Generate JWT token AND SENT OUT")
        return redirect(f"http://127.0.0.1:5001/authenticate?token={jwt_token}")

    # If there is a JWT token, validate and decode it
    with open("keys/server_public_key.pem", "rb") as file:
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
