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
                             is_valid_email, extract_jwt_token_from_args, EmailError, InvalidTokenError, MissingTokenError)
from jwt_utils import (get_jwt_redirect_url, decode_jwt_token, extract_jwt_token,
                       JWTError, SessionError, JWTAppIdMissingError, JWTPublicKeyNotFoundError)
from error_handlers import register_error_handlers

logging.basicConfig(level=logging.DEBUG)

# Load multiple public keys from files
KEYS_DIRECTORY = Path('tests/test_public_keys')
KEY_VALUE = os.getenv('SECRET_KEY', '')

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = KEY_VALUE # This is specifically used by the flask_jwt_extended extension to encode and decode JWT tokens.
app.config['SECRET_KEY'] = KEY_VALUE #  This is used by Flask for signing session cookies.
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)
jwt = JWTManager(app)
load_dotenv()

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

register_error_handlers(app) # Registers custom error handlers for the Flask app to handle application-specific exceptions.

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

    # Check if the user is already authenticated based on session data.
    if check_session_authentication(session):
        return jsonify({'message': 'User is authenticated.'}), 200

    # Try to extract JWT token from the request.
    jwt_token = extract_jwt_token(request)

    # If a JWT token is found, decode and validate it.
    if jwt_token:
        try:
            # Decode the JWT token using the public key directory.
            decoded_token = decode_jwt_token(jwt_token, KEYS_DIRECTORY)
             # Store the redirect URL from the decoded token into the session.
            session['redirect_url'] = decoded_token['redirect_url']
        except JWTAppIdMissingError as exc:
             # Handle case when the JWT token is missing the app_id claim.
            raise JWTAppIdMissingError("Error: The JWT is missing an app_id.") from exc
        except JWTPublicKeyNotFoundError as exc:
            # Handle case when the public key corresponding to the JWT's app_id cannot be found.
            raise JWTPublicKeyNotFoundError("Error: The public key corresponding to the JWT's app_id was not found.") from exc
        except JWTError as error:
             # Handle any other JWT-related errors.
            raise error

    # Extract email from the request data.
    email = extract_email_from_request(request)

    # Ensure that an email was provided in the request.
    if not email:
        raise EmailError("Missing email.")

    # Validate the provided email address.
    if not is_valid_email(email):
        raise EmailError("Invalid email address.")

    # Retrieve the redirect URL stored in the session.
    redirect_url = get_jwt_redirect_url(session)
    
    # Ensure that a redirect URL is available in the session.
    if not redirect_url:
        raise SessionError("No redirect URL set.")

     # Create a new JWT token with the email as the identity and the redirect URL as an additional claim.
    additional_claims = {"redirect_url": redirect_url}
    access_token = create_access_token(identity=email, additional_claims=additional_claims)
    # Construct the verification URL which includes the new JWT token.
    verification_url = url_for('verify_token', token=access_token, _external=True)

    print(verification_url)
    return jsonify({'message': 'Valid email address. Email sent with JWT link.'}), 200


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

        decoded_token = decode_token(token)  # This will raise jwt_exceptions.InvalidTokenError if the token is invalid.
        print("Decoded token:", decoded_token)
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        # Redirect to the extracted URL
        response = make_response(redirect(redirect_url, code=302))
        return response

    except MissingTokenError as exc:
        # Handle MissingTokenError specifically, if needed.
        # Though this is optional because the Flask app's error handler will already handle this exception.
        print("Handling MissingTokenError in verify_token")
        raise exc
    except jwt_exceptions.InvalidTokenError as exc:
        # Explicitly raise our custom InvalidTokenError exception with added context.
        raise InvalidTokenError("Invalid JWT token.") from exc


if __name__ == '__main__':
    app.run(debug=True)
