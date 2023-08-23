"""
CFIA Louis Backend Flask Application
"""
import logging
from datetime import timedelta
from pathlib import Path
import os
import uuid
import traceback
import time
from jwt import exceptions as jwt_exceptions
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask import Flask, request, jsonify, session, make_response, redirect, url_for
from flask_session import Session
from request_helpers import (extract_and_validate_request_data, check_session_authentication,
                             extract_jwt_token_from_args, InvalidTokenError,
                             MissingTokenError, RequestError)
from jwt_utils import (decode_jwt_token, extract_jwt_token, encode_jwt_token,
                       JWTError)
from error_handlers import register_error_handlers

logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure JWT-related settings
KEY_VALUE = os.getenv('SECRET_KEY') or str(uuid.uuid4())
app.config['JWT_SECRET_KEY'] = KEY_VALUE  # Used by flask_jwt_extended for encoding/decoding JWT tokens.
app.config['SECRET_KEY'] = KEY_VALUE  # Used by Flask for signing session cookies.
jwt_expiration_minutes = os.getenv('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', default="60")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(jwt_expiration_minutes))
app.config['SESSION_COOKIE_SECURE'] = True # Session cookie is only sent over HTTPS
jwt = JWTManager(app)

# Configuration for public keys
keys_directory_path_public = os.getenv('PUBLIC_KEYS_DIRECTORY', default='tests/test_public_keys')
PUBLIC_KEYS_DIRECTORY = Path(keys_directory_path_public)

# Configuration for private keys
keys_directory_path_private = os.getenv('PRIVATE_KEYS_DIRECTORY', default='tests/test_private_keys')
PRIVATE_KEYS_DIRECTORY = Path(keys_directory_path_private)

# Retrieve the application ID from environment variables; default to 'test2' if not set
APP_ID = os.getenv('APP_ID', default='test2')
private_key_path = PRIVATE_KEYS_DIRECTORY / f"{APP_ID}_private_key.pem"

# Check if the private key file exists for the given APP_ID
if not private_key_path.exists():
    raise ValueError(f"No private key found for APP_ID: {APP_ID}")

# Check if the directories exist
if not PUBLIC_KEYS_DIRECTORY.exists():
    raise ValueError(f"The directory {PUBLIC_KEYS_DIRECTORY} for public keys does not exist. Please specify a valid directory.")

if not PRIVATE_KEYS_DIRECTORY.exists():
    raise ValueError(f"The directory {PRIVATE_KEYS_DIRECTORY} for private keys does not exist. Please specify a valid directory.")


# Configure Flask-Session
app.config['SESSION_TYPE'] = os.getenv('SESSION_TYPE', default='filesystem')
Session(app)

# Register custom error handlers for the Flask app
register_error_handlers(app)

@app.before_request
def log_request_info():
    """Log incoming request headers and body for debugging purposes."""
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticate the user based on the JWT token from the URL parameter and the email from 
    the request body.
    
    1. Checks if the user is already authenticated.
    2. Validates and decodes the provided JWT token to set the redirect URL in the session.
    3. Verifies the email address from the request payload.
    4. If the email is valid, creates a new access token and responds with a message.
    
    Returns:
        - JSON response with an appropriate message based on the authentication status.
        - Relevant HTTP status codes indicating the success or error of the request.
    """
    logging.debug("Session Data: %s", session)

    try:
        # Check if the user is already authenticated based on session data.
        if check_session_authentication(session):
            return jsonify({'message': 'User is authenticated.'}), 200

        # Try to extract JWT token from the request.
        jwt_token = extract_jwt_token(request)

        # If a JWT token is found, decode and validate it.
        if jwt_token:
            # Decode the JWT token using the public key directory.
            decoded_token = decode_jwt_token(jwt_token, PUBLIC_KEYS_DIRECTORY)
            # Store the redirect URL from the decoded token into the session.
            session['redirect_url'] = decoded_token['redirect_url']

        # Extract and validate email and redirect URL from the request and session.
        email, redirect_url = extract_and_validate_request_data(request, session)

        # Create the payload with the email as the identity and the redirect URL as an additional claim.
        expiration_time = time.time() + 900  # Token will be valid for 15 minutes
        
        payload = {
            "sub": email,
            "redirect_url": redirect_url,
            "app_id": APP_ID,  # Replace 'test2' with the appropriate app ID
            "exp": expiration_time
        }

        current_private_key_path  = PRIVATE_KEYS_DIRECTORY / f"{APP_ID}_private_key.pem"
        jwt_token = encode_jwt_token(payload, current_private_key_path )

        # Construct the verification URL which includes the new JWT token.
        verification_url = url_for('verify_token', token=jwt_token, _external=True)
        print(verification_url)
        return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200

    except (JWTError, RequestError) as error:
        # Capture the stack trace
        stack_trace = traceback.format_exc()
        app.logger.error("Exception occurred: %s", stack_trace)
        return jsonify({'error': str(error)}), 400  # Return a 400 Bad Request with the error message.

@app.route('/verify_token', methods=['GET'])
def verify_token():
    """
    Handle the verification of the JWT token received via the link.
    Returns:
        - If the token is valid and not expired, set the session variables
          'authenticated' and 'user_email' and redirect the user to the dashboard.
        - If the token is expired or invalid, return a JSON response with an error message.
    """
    try:
        token = extract_jwt_token_from_args(request)  # This can raise MissingTokenError.

        decoded_token = decode_jwt_token(token, PUBLIC_KEYS_DIRECTORY)
        print("Decoded token:", decoded_token)
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        # Redirect to the extracted URL
        response = make_response(redirect(redirect_url, code=302))
        return response

    except (MissingTokenError, InvalidTokenError, jwt_exceptions.InvalidTokenError) as error:
        # Print the stack trace for debugging purposes
        print(traceback.format_exc())

        error_message = str(error)
        if isinstance(error, jwt_exceptions.InvalidTokenError):
            error_message = "Invalid JWT token."
        return jsonify({'error': error_message}), 400

if __name__ == '__main__':
    app.run(debug=True)
