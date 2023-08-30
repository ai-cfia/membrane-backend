import os
from flask import Flask, redirect, request, session, url_for
import jwt
from generate_jwt import generate_jwt

app = Flask(__name__)

# Generate a secret key for the session cookie
app.secret_key = os.urandom(24)

def decode_jwt_token(jwt_token, public_key):
    """
    Decoding the JWT using the given public key.
    """
    try:
        decoded_token = jwt.decode(jwt_token, public_key, algorithms=['RS256'])
        return decoded_token
    except Exception as error:
        print(f"Error decoding JWT: {error}")
        return None
    
@app.route('/')
def hello_world():
    # Check if there's a session cookie
    if 'authenticated' in session and session['authenticated']:
        print("Stage FINAL SHOW HOME PAGE")
        return 'Hello World!'

    # Check if there's a JWT token in the request from another backend
    jwt_token = request.args.get('token')
    if not jwt_token:
        # Generate JWT token
        with open('tests/client_private_keys/testapp1_private_key.pem', 'rb') as file:
            private_key_content = file.read()
        data = {
            "app_id": "testapp1",
            "redirect_url": url_for("hello_world", _external=True)
        }
        jwt_token = generate_jwt(data, private_key_content)
        # Redirect to /authenticate with the generated JWT token
        print("Generate JWT token AND SENT OUT")
        return redirect(f"http://127.0.0.1:5000/authenticate?token={jwt_token}")

    # If there is a JWT token, validate and decode it
    with open('tests/server_public_key/server_public_key.pem', 'rb') as file:
        public_key_content = file.read()
    
    decoded_token = decode_jwt_token(jwt_token, public_key_content)

    if decoded_token:
        # If the JWT token is valid, generate a session cookie
        print("JWT token VALID")
        session['authenticated'] = True
        return redirect(url_for("hello_world"))

    return 'Invalid Token!'


if __name__ == '__main__':
    app.run(debug=True)
