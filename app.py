"""
CFIA Louis Backend Flask Application
"""
import logging
from datetime import timedelta
from pathlib import Path
from jwt import decode, exceptions as jwt_exceptions
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, create_access_token, decode_token
from flask import Flask, request, jsonify, session, make_response, redirect, url_for
from flask_session import Session
from utils import is_valid_email

logging.basicConfig(level=logging.DEBUG)

with open('keys/public_key.pem', 'rb') as f:
    PUBLIC_KEY = f.read()

KEY_VALUE = 'super-secret'
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = KEY_VALUE
app.config['SECRET_KEY'] = KEY_VALUE
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
app.config['PUBLIC_KEY'] = PUBLIC_KEY
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
    data = request.get_json()
    email = data.get('email')

    logging.debug("Session Data: %s", session)

    # Check session
    if 'authenticated' in session and session['authenticated']:
        return jsonify({'message': 'User is authenticated.'}), 200

    # Extracting JWT token from the URL parameter
    jwt_token = request.args.get('token')

    # If the token is missing, raise an error
    if not jwt_token:
        return jsonify({'error': 'No JWT provided.'}), 400

    # Decoding the token and setting the redirect URL
    try:
        decoded_token = decode(jwt_token, app.config['PUBLIC_KEY'], algorithms=['RS256'])
        if 'redirect_url' not in decoded_token:
            logging.error('JWT Token does not contain redirect_url')
            return jsonify({'error': 'Token does not contain a redirect URL'}), 400
        session['redirect_url'] = decoded_token['redirect_url']

    except jwt_exceptions.ExpiredSignatureError:
        logging.exception('JWT Token has expired')
        return jsonify({'error': 'Token has expired'}), 400

    except jwt_exceptions.InvalidTokenError as error:
        logging.exception('JWT Token decoding error: %s', error)
        return jsonify({'error': f'Invalid token. Reason: {str(error)}'}), 400

    except Exception as error:
        logging.exception('Unexpected error while processing token: %s', error)
        return jsonify({'error': f'Unexpected error: {str(error)}'}), 500

    # Check if email exists and validate
    if email is None:
        return jsonify({'error': 'Missing email.'}), 400

    if is_valid_email(email):
        redirect_url = session.get('redirect_url')
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
        decoded_token = decode_token(token)
        print("Decoded token:", decoded_token)
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']

        session['authenticated'] = True
        session['user_email'] = email

        response = make_response(redirect(redirect_url, code=302))
        return response

    except jwt_exceptions.InvalidTokenError as invalid_token_error:
        logging.error('JWT Token decoding error: %s', invalid_token_error)
        return jsonify({'error': 'Invalid token.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
