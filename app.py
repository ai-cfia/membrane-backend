"""
CFIA Louis Backend Flask Application
"""
import logging
from datetime import timedelta, datetime
from pathlib import Path
import os
import uuid
import traceback
from flask_cors import CORS
from jwt import exceptions as jwt_exceptions
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from flask import Flask, request, jsonify, session, make_response, redirect, url_for
from flask_session import Session
from request_helpers import (validate_email_from_request, check_session_authentication,
                             InvalidTokenError, MissingTokenError, EmailError)
from jwt_utils import (decode_jwt_token, encode_email_token, decode_email_token,
                       JWTError, JWTExpired)
from environment_validation import validate_environment_settings
from error_handlers import register_error_handlers

logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)

# Allow CORS for your Flask app
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

# Load environment variables
load_dotenv()

# Configuration for JWT and session settings
# Fetch secret key or generate a new one if not available
SECRET_KEY = os.getenv('SECRET_KEY', str(uuid.uuid4()))
# Set secret key configurations for JWT and Flask session
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY

# Configure JWT expiration from environment variable with default of 30 minutes
jwt_expiration_minutes = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 30))

# Configure session lifetime from environment variable with default of 30 minutes
session_lifetime_minutes = int(os.environ.get('SESSION_LIFETIME_MINUTES', 30))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=session_lifetime_minutes)

# Configure session cookie to be secure (sent over HTTPS only)
app.config['SESSION_COOKIE_SECURE'] = True

# Initialize JWT Manager with the app
jwt = JWTManager(app)

# Configuration paths and URLs retrieved from environment variables # TODO: Set default values
CLIENT_PUBLIC_KEYS_DIRECTORY = Path(os.getenv('CLIENT_PUBLIC_KEYS_DIRECTORY', 'keys/public_keys'))
SERVER_PRIVATE_KEY = Path(os.getenv('SERVER_PRIVATE_KEY', ''))
SERVER_PUBLIC_KEY = Path(os.getenv('SERVER_PUBLIC_KEY', ''))
REDIRECT_URL_TO_LOUIS_FRONTEND = os.getenv('REDIRECT_URL_TO_LOUIS_FRONTEND', '')

# Validate the environment settings
validate_environment_settings(
    CLIENT_PUBLIC_KEYS_DIRECTORY,
    SERVER_PRIVATE_KEY, 
    SERVER_PUBLIC_KEY, 
    REDIRECT_URL_TO_LOUIS_FRONTEND
)

# A basic in-memory store for simplicity;
TOKEN_BLACKLIST = set()

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

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    try:
        state = session.get('state', 'INITIAL_STATE')

        if state == 'INITIAL_STATE':
            print('STATE 1')

            # Try to extract and decode JWT token from the request.
            clientapp_token = request.args.get('token')
            clientapp_decoded_token = decode_jwt_token(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY)

            # If a valid JWT token is found, update the session and prepare a redirect response.
            if clientapp_decoded_token:
                session['state'] = 'AWAITING_EMAIL'
                redirect_url_with_token = f"{REDIRECT_URL_TO_LOUIS_FRONTEND}?token={clientapp_token}"
                response = redirect(redirect_url_with_token)
            else:
                response = jsonify({'message': 'Invalid JWT Provided'}), 400

            return response

        if state == 'AWAITING_EMAIL':
            print('STATE 2')

            # Retrieve and decode URL query token from client app
            clientapp_token = request.args.get('token')
            clientapp_decoded_token = decode_jwt_token(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY)

            if not clientapp_decoded_token:
                raise JWTError('Invalid JWT in session.')

            if request.is_json:
                # Extract the email from the request data and validate it.
                email = validate_email_from_request(request.get_json().get('email'))
            else:
                redirect_url_with_invalid_email = f"{REDIRECT_URL_TO_LOUIS_FRONTEND}?token={clientapp_token}"
                return redirect(redirect_url_with_invalid_email)

            expiration_time = datetime.utcnow() + timedelta(minutes=jwt_expiration_minutes)
            expiration_timestamp = int(expiration_time.timestamp())

            payload = {
                "sub": email,
                "redirect_url": clientapp_decoded_token['redirect_url'],
                "exp": expiration_timestamp
            }

            email_token = encode_email_token(payload, SERVER_PRIVATE_KEY)

            # Construct the verification URL which includes the new JWT token.
            verification_url = url_for('authenticate', token=email_token, _external=True)
            print(verification_url)  # Debug purpose; remove or comment out for production.

            # TODO: Send email to user containing verification url.
            session['state'] = 'EMAIL_SENT'
            return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200

        if state == 'EMAIL_SENT':
            # Debugging purposes;
            print('STATE 3')

            # Extract the JWT token from the request.
            email_token = request.args.get('token')     
            try:
                decoded_email_token = decode_email_token(email_token, SERVER_PUBLIC_KEY, TOKEN_BLACKLIST)

            except Exception as error:
                # Catch other exceptions for debugging
                print("Type of error:", type(error))
                print("Unexpected error in decode_email_token:", str(error))
                session['state'] = 'AWAITING_EMAIL'
                redirect_url_with_invalid_email = f"{REDIRECT_URL_TO_LOUIS_FRONTEND}?token={email_token}"
                return redirect(redirect_url_with_invalid_email)

            # If a valid email token is decoded, proceed to validate and use it.
            TOKEN_BLACKLIST.add(email_token)
            session['authenticated'] = True
            session['state'] = 'USER_AUTHENTICATED'
            email_token_redirect = f"{decoded_email_token['redirect_url']}?token={email_token}"
            response = make_response(redirect(email_token_redirect, code=302))

            return response

        if state == 'USER_AUTHENTICATED':
            print('STATE 4')

            if check_session_authentication(session):
                return jsonify({'message': 'User is authenticated.'}), 200

            session['state'] = 'INITIAL_STATE'
            return jsonify({'message': 'Session has expired, user is not authenticated.'}), 200

    except (JWTError, JWTExpired, MissingTokenError, InvalidTokenError, jwt_exceptions.ExpiredSignatureError,
            EmailError, jwt_exceptions.InvalidTokenError) as error:
        logging.error(traceback.format_exc())

        # Handle the JWT expiration error specifically
        if isinstance(error, JWTExpired) and str(error) == "JWT token has expired.":
            print("JWT EXPIRED")
            session['state'] = 'INITIAL_STATE'
            return jsonify({'message': 'JWT token has expired, new authentication required.'}), 401

        # Handle specific case for InvalidTokenError during EMAIL_SENT state
        if isinstance(error, InvalidTokenError) and session.get('state') == 'EMAIL_SENT':
            print("INVALID TOKEN")
            session['state'] = 'AWAITING_EMAIL'
            redirect_url_with_invalid_email = f"{REDIRECT_URL_TO_LOUIS_FRONTEND}?token={email_token}"
            return redirect(redirect_url_with_invalid_email)

        error_message_map = {
            jwt_exceptions.ExpiredSignatureError: "Expired JWT token.",
            jwt_exceptions.InvalidTokenError: "Invalid JWT token."
        }
        error_message = error_message_map.get(type(error), str(error))
        return jsonify({'error': error_message}), 400
    # This is the default return statement that will be executed
    # if neither POST nor GET conditions are met.
    return jsonify({'error': 'Invalid request method'}), 405  # 405 is for Method Not Allowed

if __name__ == '__main__':
    app.run(debug=True)
