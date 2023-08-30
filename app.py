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
from jwt_utils import (decode_jwt_token, encode_jwt_token,
                       JWTError, JWTExpired)
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

# Configuration for client public keys

CLIENT_PUBLIC_KEYS_DIRECTORY = Path(os.getenv('CLIENT_PUBLIC_KEYS_DIRECTORY', default='keys/public_keys'))
# Retrieve server private/public key paths from environment variables; default to '' if not set
SERVER_PRIVATE_KEYS_DIRECTORY = Path(os.getenv('SERVER_PRIVATE_KEYS_DIRECTORY', default=''))  # TODO: Set default
SERVER_PUBLIC_KEYS_DIRECTORY = Path(os.getenv('SERVER_PUBLIC_KEYS_DIRECTORY', default=''))    # TODO: Set default
# Retrieve server private key name from environment variable; default to '' if not set
SERVER_PRIVATE_KEY = os.getenv('SERVER_PRIVATE_KEY', default='') #TODO: Set default value
# Retrieve redirect URL to Louis Frontend
REDIRECT_URL_TO_LOUIS_FRONTEND = os.environ.get('REDIRECT_URL_TO_LOUIS_FRONTEND', '') #TODO: Set default value

# Check if the directories exist
if not Path(CLIENT_PUBLIC_KEYS_DIRECTORY).exists():
    raise ValueError(f"The directory {CLIENT_PUBLIC_KEYS_DIRECTORY} for public keys does not exist. Please specify a valid directory.")
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

@app.route('/check_session', methods=['GET'])
def check_session():
    """ Check if the user is already authenticated based on session data."""
    if check_session_authentication(session):
        return jsonify({'message': 'User is authenticated.'}), 200

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    """
    Authenticates a user based on the provided JWT token.
    The JWT token is extracted from the request's `token` parameter. 
    This function also checks the session to handle different stages 
    of the authentication process. If the JWT token is valid, the user 
    is authenticated.  
    """
    try:
        state = session.get('state', 'INITIAL_STATE')

        if state == 'INITIAL_STATE':
            print('STATE 1')
            # Try to extract JWT token from the request.
            clientapp_token = request.args.get('token')
            clientapp_decoded_token = decode_jwt_token(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY, TOKEN_BLACKLIST)

            # If a JWT token is found, decode and validate it.
            if clientapp_decoded_token:
                # Store the JWT into the session.
                session['JWT'] = clientapp_token
                session['state'] = 'Awaiting_Email'
                # Redirect to the desired URL
                return redirect(REDIRECT_URL_TO_LOUIS_FRONTEND)

            return jsonify({'message': 'Invalid JWT Provided'}), 400

        if state == 'Awaiting_Email':
            logging.debug("Session Data: %s", session)
            print('STATE 2')

            # Extract email from the request data.
            email = request.get_json().get('email')
            
            # Decode the JWT token using the public key directory.
            decoded_token = decode_jwt_token(session['JWT'], CLIENT_PUBLIC_KEYS_DIRECTORY, TOKEN_BLACKLIST)

            if decoded_token:
                
                email = validate_email_from_request(email)
                expiration_time = datetime.utcnow() + timedelta(minutes=jwt_expiration_minutes)
                expiration_timestamp = int(expiration_time.timestamp())

                payload = {
                    "sub": email,
                    "redirect_url": decoded_token['redirect_url'],
                    "app_id": SERVER_PRIVATE_KEY,
                    "exp": expiration_timestamp
                }

                current_server_private_key_path = SERVER_PRIVATE_KEYS_DIRECTORY / f"{SERVER_PRIVATE_KEY}_private_key.pem"
                jwt_token = encode_jwt_token(payload, current_server_private_key_path)

                # Construct the verification URL which includes the new JWT token.
                verification_url = url_for('authenticate', token=jwt_token, _external=True)
                print(verification_url)

                # TODO: Send email to user containing verification url.
                session['state'] = 'Email_Sent'
                return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200

        if state == 'Email_Sent':
            # Try to extract JWT token from the request.
            email_token = request.args.get('token')
            decoded_token = decode_jwt_token(email_token, SERVER_PUBLIC_KEYS_DIRECTORY, TOKEN_BLACKLIST)
            print('STATE 3')

            # If a email token is found, decode and validate it.
            if decoded_token:
                # Decode the email token using the public key directory.
                TOKEN_BLACKLIST.add(email_token)
                session['authenticated'] = True
                session['state'] = 'USER_AUTHENTICATED'
                email_token_redirect = f"{decoded_token['redirect_url']}?token={email_token}"
                return make_response(redirect(email_token_redirect, code=302))

        if state == 'USER_AUTHENTICATED':
            if check_session_authentication(session):
                return jsonify({'message': 'User is authenticated.'}), 200

            session['state'] = 'INITIAL_STATE'
            return jsonify({'message': 'Session has expired, user is not authenticated.'}), 200

    except (JWTError, JWTExpired, MissingTokenError, InvalidTokenError, jwt_exceptions.ExpiredSignatureError,
            EmailError, jwt_exceptions.InvalidTokenError) as error:
        logging.error(traceback.format_exc())
        print('STATE 4')

        # Handle the JWT expiration error specifically
        if isinstance(error, JWTExpired) and str(error) == "JWT token has expired.":
            session['state'] = 'INITIAL_STATE'
            return jsonify({'message': 'JWT token has expired, new authentication required.'}), 401

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
