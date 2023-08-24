"""
CFIA Louis Backend Flask Application
"""
import logging
from datetime import timedelta, datetime
from pathlib import Path
import os
import uuid
import traceback
from jwt import exceptions as jwt_exceptions
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask import Flask, request, jsonify, session, make_response, redirect, url_for
from flask_session import Session
from request_helpers import (extract_email_from_request, check_session_authentication,
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

# Configuration for JWT and session settings
# Fetch secret key or generate a new one if not available
KEY_VALUE = os.getenv('SECRET_KEY', str(uuid.uuid4()))
# Set secret key configurations for JWT and Flask session
app.config['JWT_SECRET_KEY'] = KEY_VALUE
app.config['SECRET_KEY'] = KEY_VALUE

# Configure JWT expiration from environment variable with default of 30 minutes
jwt_expiration_minutes = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 30))

# Configure session lifetime from environment variable with default of 30 minutes
session_lifetime_minutes = int(os.environ.get('SESSION_LIFETIME_MINUTES', 30))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=session_lifetime_minutes)

# Configure session cookie to be secure (sent over HTTPS only)
app.config['SESSION_COOKIE_SECURE'] = True

# Initialize JWT Manager with the app
jwt = JWTManager(app)

# Configuration for public keys
keys_directory_path_public = os.getenv('PUBLIC_KEYS_DIRECTORY', default='keys/public_keys')
PUBLIC_KEYS_DIRECTORY = Path(keys_directory_path_public)

# Configuration for private keys
keys_directory_path_private = os.getenv('PRIVATE_KEYS_DIRECTORY', default='keys/private_keys')
PRIVATE_KEYS_DIRECTORY = Path(keys_directory_path_private)

# Retrieve the application ID from environment variables; default to '' if not set
APP_ID = os.getenv('APP_ID', default='') #TODO: Set default value
private_key_path = PRIVATE_KEYS_DIRECTORY / f"{APP_ID}_private_key.pem"

# Check if the private key file exists for the given APP_ID
if not private_key_path.exists():
    raise ValueError(f"No private key found for APP_ID: {APP_ID}")

# Check if the directories exist
if not PUBLIC_KEYS_DIRECTORY.exists():
    raise ValueError(f"The directory {PUBLIC_KEYS_DIRECTORY} for public keys does not exist. Please specify a valid directory.")

if not PRIVATE_KEYS_DIRECTORY.exists():
    raise ValueError(f"The directory {PRIVATE_KEYS_DIRECTORY} for private keys does not exist. Please specify a valid directory.")


TOKEN_BLACKLIST = set()  # A basic in-memory store for simplicity;

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
        jwt_token = extract_jwt_token(request, session)

        # If a JWT token is found, decode and validate it.
        if jwt_token:
            # Decode the JWT token using the public key directory.
            decoded_token = decode_jwt_token(jwt_token, PUBLIC_KEYS_DIRECTORY)
            # Store the redirect URL from the decoded token into the session.
            session['redirect_url'] = decoded_token['redirect_url']

        # Extract and validate email and redirect URL from the request and session.
        email = extract_email_from_request(request)
        # Create the payload with the email as the identity and the redirect URL as an additional claim.
        print("JWT Expiry set for:", jwt_expiration_minutes, "minutes")
        expiration_time = datetime.utcnow() + timedelta(minutes=jwt_expiration_minutes)
        expiration_timestamp = int(expiration_time.timestamp())
        print("expiration time: " + str(expiration_timestamp))
        payload = {
            "sub": email,
            "redirect_url": session['redirect_url'],
            "app_id": APP_ID,
            "exp": expiration_timestamp
        }

        current_private_key_path  = PRIVATE_KEYS_DIRECTORY / f"{APP_ID}_private_key.pem"
        jwt_token = encode_jwt_token(payload, current_private_key_path )

        # Construct the verification URL which includes the new JWT token.
        verification_url = url_for('verify_token', token=jwt_token, _external=True)
        print(verification_url)
        #TODO: Send email to user containing verification url.
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
        token = extract_jwt_token_from_args(request, TOKEN_BLACKLIST)
        # After successful verification, add token to blacklist.
        TOKEN_BLACKLIST.add(token)

        # Decode token
        decoded_token = decode_jwt_token(token, PUBLIC_KEYS_DIRECTORY)
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']
        print(redirect_url)

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        # Redirect to the extracted URL
        response = make_response(redirect(redirect_url, code=302))
        return response

    except (JWTError, MissingTokenError, InvalidTokenError, jwt_exceptions.ExpiredSignatureError, jwt_exceptions.InvalidTokenError) as error:
        # Print the stack trace for debugging purposes
        print(traceback.format_exc())
        if isinstance(error, jwt_exceptions.ExpiredSignatureError):
            error_message = "Expired JWT token."
        elif isinstance(error, jwt_exceptions.InvalidTokenError):
            error_message = "Invalid JWT token."
        else:
            error_message = str(error)
        return jsonify({'error': error_message}), 400

if __name__ == '__main__':
    app.run(debug=True)
