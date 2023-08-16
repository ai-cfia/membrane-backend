"""
CFIA Louis Backend Flask Application
"""
import logging
from datetime import timedelta
from pathlib import Path
import os
from jwt import exceptions as jwt_exceptions
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from flask import Flask, request, jsonify, session, make_response, redirect, url_for
from flask_session import Session
from request_helpers import (extract_email_from_request, check_session_authentication,
                             is_valid_email)
from jwt_utils import (load_keys_from_directory, get_jwt_redirect_url, decode_jwt_token,
                       extract_jwt_token, watch_keys_directory)
logging.basicConfig(level=logging.DEBUG)

# Load multiple public keys from files
KEYS_DIRECTORY = Path('tests/test_public_keys')
KEYS = load_keys_from_directory(KEYS_DIRECTORY)

KEY_VALUE = os.getenv('SECRET_KEY', '')
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = KEY_VALUE
"""
Note:  
app.config['JWT_SECRET_KEY']: This is specifically used by the flask_jwt_extended extension to 
encode and decode JWT tokens. This ensures that the JWT tokens remain tamper-proof.
"""
app.config['SECRET_KEY'] = KEY_VALUE
"""
Note: 
'app.config['SECRET_KEY']': This is typically used by Flask for signing session cookies. If you're 
using Flask's built-in session system (or Flask-Session with some storage types), you'll need 
this key. This key ensures that data stored in user sessions remains tamper-proof between requests.
"""
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
app.config['PUBLIC_KEYS'] = KEYS
jwt = JWTManager(app)
env_path = Path('./') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

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
    jwt_token = extract_jwt_token(request)
    email = extract_email_from_request(request)

    logging.debug("Session Data: %s", session)

    if check_session_authentication(session):
        return jsonify({'message': 'User is authenticated.'}), 200

    if jwt_token:
        decoded_token, error = decode_jwt_token(jwt_token, KEYS)
        if error:
            return jsonify(error), 400
        session['redirect_url'] = decoded_token['redirect_url']

    if not email:
        return jsonify({'error': 'Missing email.'}), 400

    if is_valid_email(email):
        redirect_url = get_jwt_redirect_url(session)
        if not redirect_url:
            return jsonify({'error': 'No redirect URL set.'}), 400

        additional_claims = {"redirect_url": redirect_url}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        verification_url = url_for('verify_token', token=access_token, _external=True)

        print(verification_url)
        return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200

    return jsonify({'error': 'Invalid email address.'}), 400

@app.route('/verify_token', methods=['GET'])
def verify_token():
    """
    Handle the verification of the JWT token received via the link.
    Returns:
        - If the token is valid and not expired, set the session variables
          'authenticated' and 'user_email' and redirect the user to the dashboard.
        - If the token is expired or invalid, return a JSON response with an error message.
    """
    token = request.args.get('token')  # Extract token from URL parameters

    if token is None:
        return jsonify({'error': 'No token provided.'}), 400

    try:
        print("Received token:", token)
        # Decode and verify the JWT token using the app's secret key
        decoded_token = decode_token(token)
        print("Decoded token:", decoded_token)
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        # Redirect to the extracted URL
        response = make_response(redirect(redirect_url, code=302))
        return response

    except jwt_exceptions.InvalidTokenError as invalid_token_error:
        # Log the exception message to inspect the reason for the decoding failure
        logging.error('JWT Token decoding error: %s', invalid_token_error)
        return jsonify({'error': 'Invalid token.'}), 400

@app.route('/reload_keys', methods=['GET'])
def reload_keys_endpoint():
    '''Endpoint to manually reload keys when the keys directory changes.'''
    reload_keys()
    return jsonify({"message": "Keys reloaded successfully."}), 200

def reload_keys():
    """Callback function to reload keys when the keys directory changes."""
    global KEYS
    KEYS = load_keys_from_directory(KEYS_DIRECTORY)

if __name__ == '__main__':
    # Watch the KEYS_DIRECTORY for changes and reload keys when changes occur.
    watch_keys_directory(KEYS_DIRECTORY, reload_keys)
    app.run(debug=True)
