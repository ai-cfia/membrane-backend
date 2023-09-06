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
from flask import Flask, request, jsonify, session, url_for
from flask_session import Session
from request_helpers import (validate_email_from_request, check_session_authentication,
                             InvalidTokenError, MissingTokenError, EmailError)
from jwt_utils import (decode_client_jwt_token, encode_email_verification_token, process_email_verification_token, login_redirect_with_client_jwt,
                       redirect_to_client_app_using_verification_token, JWTError, JWTExpired)
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
    """
    Handle user authentication based on various states and the provided JWT token.
    
    This function manages the user authentication flow by transitioning through
    various states represented by the session. Depending on the current state, 
    the function will take different actions such as validating a client app token 
    or checking the email token for authenticity. For each state, it leverages 
    corresponding handler functions. 

    The following states are managed:
    - INITIAL_STATE: Processes the initial state of the authentication flow.
    - AWAITING_EMAIL: Waits for an email token after the client app token has been processed.
    - EMAIL_SENT: Handles the state after the verification email has been sent to the user.
    - USER_AUTHENTICATED: Checks and confirms if a user is authenticated.
    
    Parameters:
    - None. However, a JWT token should be present in the request URL query parameters.
    
    Returns:
    - JSON Response: Depending on the authentication state and success of the authentication,
      it returns either a success message or an error message.
    """
    try:
        # Retrieve the current authentication state from the session.
        # Defaulting to 'INITIAL_STATE' if not set.
        state = session.get('state', 'INITIAL_STATE')

        if state == 'INITIAL_STATE':
            print('CURRENT STATE: INITIAL_STATE')
            # Extract client app token from request URL query.
            clientapp_token = request.args.get('token')
            response = handle_initial_state(clientapp_token)
            return response

        if state == 'AWAITING_EMAIL':
            # Extract client app token from request URL query.
            clientapp_token = request.args.get('token')
            response = handle_awaiting_email_state(clientapp_token)
            return response

        if state == 'EMAIL_SENT':
            # Extract the JWT token from the request.
            email_token = request.args.get('token')
            response = handle_email_sent_state(email_token)
            return response

        if state == 'USER_AUTHENTICATED':
            print('USER_AUTHENTICATED')
            if check_session_authentication(session):
                return jsonify({'message': 'User is authenticated.'}), 200

            session['state'] = 'INITIAL_STATE'
            return jsonify({'message': 'Session has expired, user is not authenticated.'}), 200

    except (JWTError, JWTExpired, MissingTokenError, InvalidTokenError, jwt_exceptions.ExpiredSignatureError,
            EmailError, jwt_exceptions.InvalidTokenError) as error:
        logging.error(traceback.format_exc())

        error_message_map = {
            jwt_exceptions.ExpiredSignatureError: "Expired JWT token.",
            jwt_exceptions.InvalidTokenError: "Invalid JWT token."
        }
        error_message = error_message_map.get(type(error), str(error))
        return jsonify({'error': error_message}), 400
    # This is the default return statement that will be executed
    # if neither POST nor GET conditions are met.
    return jsonify({'error': 'Invalid request method'}), 405  # 405 is for Method Not Allowed

def handle_initial_state(clientapp_token):
    """
    Handles the logic for when the state is INITIAL_STATE.
    Attempts to redirect the user based on the provided JWT or verification token.
    """
    try:
        session['state'] = 'AWAITING_EMAIL'
        print('CURRENT STATE: AWAITING_EMAIL')
        # Attempt to decode the JWT from the client application and redirect to Louis Login Frontend.
        # Token then gets passed on in the redirect.
        response = login_redirect_with_client_jwt(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY, REDIRECT_URL_TO_LOUIS_FRONTEND)
        return response
    except Exception:
        logging.exception("Failed during login redirect with client jwt")

    # Attempt to handle the case where a verification email token is passed in the request URL.    
    # In case user has clicked on the verification URL and the application state = INITIAL_STATE.
    try:
        return redirect_to_client_app_using_verification_token(clientapp_token, SERVER_PUBLIC_KEY, TOKEN_BLACKLIST)
    except Exception as error:
        print("Something went wrong. Type of error:", type(error))
        # TODO: Redirect to Louis main site because tokens are all expired.

    return jsonify({'message': 'Invalid JWT Provided'}), 400

def handle_awaiting_email_state(clientapp_token):
    """
    Handles the logic for when the state is AWAITING_EMAIL.
    Attempts to decode the client JWT and sends an email verification link if an email is provided.
    """
    try:
        clientapp_decoded_token = decode_client_jwt_token(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY)

        # If the request contains an email parameter provided by the user.
        if request.is_json:
            # Validate email.
            email = validate_email_from_request(request.get_json().get('email'))
            # Generate token expiration timestamp.
            expiration_time = datetime.utcnow() + timedelta(minutes=jwt_expiration_minutes)
            expiration_timestamp = int(expiration_time.timestamp())

            # Token payload.
            payload = {
                "sub": email,
                "redirect_url": clientapp_decoded_token['redirect_url'],
                "exp": expiration_timestamp
            }

            # Encode email token using the servers dedicated private key.
            email_token = encode_email_verification_token(payload, SERVER_PRIVATE_KEY)

            # Construct the verification URL which includes the new JWT token.
            verification_url = url_for('authenticate', token=email_token, _external=True)
            print(verification_url)  # Debug purpose; remove or comment out for production.

            # TODO: Send email to user containing verification url.
            session['state'] = 'EMAIL_SENT'
            print('CURRENT STATE: EMAIL_SENT')

            return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200

        # Redirect user if they reload the link without providing an email.    
        return login_redirect_with_client_jwt(clientapp_token, CLIENT_PUBLIC_KEYS_DIRECTORY, REDIRECT_URL_TO_LOUIS_FRONTEND)

    except Exception:
        try:
            return redirect_to_client_app_using_verification_token(clientapp_token, SERVER_PUBLIC_KEY, TOKEN_BLACKLIST)
        except Exception as error:
            print("Something went wrong. Type of error:", type(error))
            # TODO: Redirect to Louis main site because tokens are all expired.

    return jsonify({'message': 'Invalid JWT Provided'}), 400

def handle_email_sent_state(email_token):
    """
    Handles the logic for when the state is EMAIL_SENT.
    Tries processing the email verification token and attempts a redirect using the client JWT if that fails.
    """
    try:
        return process_email_verification_token(email_token, SERVER_PUBLIC_KEY, TOKEN_BLACKLIST)
    except Exception as error:
        logging.error("Failed during decoding or initial operations. Type of error: %s", type(error))
        
        # Attempt redirect using the client JWT.
        try:
            return login_redirect_with_client_jwt(email_token, CLIENT_PUBLIC_KEYS_DIRECTORY, REDIRECT_URL_TO_LOUIS_FRONTEND)
        except Exception as redirect_error:
            logging.error("Failed during redirect with client jwt. Type of error: %s", type(redirect_error))

    return jsonify({'message': 'Invalid JWT Provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
