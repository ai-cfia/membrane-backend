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
app.config['JWT_SECRET_KEY'] = KEY_VALUE  # Change this!
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
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=60)  # Set token expiry time
app.config['PUBLIC_KEY'] = PUBLIC_KEY
jwt = JWTManager(app)
env_path = Path('./') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.before_request
def log_request_info():
    """
    This function logs the request info.
    
    It is executed before each request in the Flask application due 
    to the use of the @app.before_request decorator.
    """
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.route('/set_redirect_url', methods=['POST'])
def set_redirect_url():
    """
    Set a redirect URL based on the JWT token provided in the request.

    The function expects a JSON body with a 'token' key containing a valid JWT.
    The JWT should contain a 'redirect_url' claim, which is extracted and stored in the session.

    Returns:
        - 200 OK if the JWT is valid and the redirect URL is set successfully.
        - 400 Bad Request if no JWT is provided or if there's a JWT decoding error.
        - 500 Internal Server Error for unexpected issues.
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify({'error': 'Invalid JSON payload.'}), 400

    jwt_token = request.get_json().get('token')
    if not jwt_token:
        return jsonify({'error': 'No JWT provided.'}), 400

    try:
        # Decode the token using the PUBLIC KEY
        decoded_token = decode(jwt_token, app.config['PUBLIC_KEY'], algorithms=['RS256'])

        if 'redirect_url' not in decoded_token:
            logging.error('JWT Token does not contain redirect_url')
            return jsonify({'error': 'Token does not contain a redirect URL'}), 400

        session['redirect_url'] = decoded_token['redirect_url']
        return jsonify({'message': 'Redirect URL set successfully.'}), 200

    except jwt_exceptions.ExpiredSignatureError:
        logging.exception('JWT Token has expired')
        return jsonify({'error': 'Token has expired'}), 400

    except jwt_exceptions.InvalidTokenError as error:
        logging.exception('JWT Token decoding error: %s', error)
        return jsonify({'error': f'Invalid token. Reason: {str(error)}'}), 400

    except Exception as error:
        logging.exception('Unexpected error while processing token: %s', error)
        return jsonify({'error': f'Unexpected error: {str(error)}'}), 500

@app.route('/check_session', methods=['GET'])
def check_session():
    """
    This endpoint checks if there is a current session for the user. If the user is 
    not authenticated, the user will be redirected to the login page.

    Parameters:
    None

    Returns:
    A JSON response object and an HTTP status code. The response object contains a 'message' key.
    The possible outcomes are:
    - Returns a 200 HTTP status code and a message that the user is authenticated if there is a 
      current session for the user.
    - TODO: Returns a redirection to the Louis Login Frontend if there is no current session for the 
      user.
    """
    # At the start of your check_session function
    logging.debug("Received Session Data: %s", session)

    if 'authenticated' in session and session['authenticated']:
        return jsonify({'message': 'User is authenticated.'}), 200

    # - TODO: Implement redirection to Louis Login Frontend
    return jsonify({'message': 'User is not authenticated. Redirecting...'}), 200

@app.route('/login', methods=['POST'])
def login():
    """
    This endpoint handles user login. It receives an email and a redirect URL via a POST request.
    If the email is valid and if the user is not already authenticated, a JWT token is created 
    and a verification URL, which includes the token as a query parameter, is sent to the user's 
    email.
    
    Parameters:
    None, but expects a JSON object in the request body with 'email' and 'redirect_url' keys.

    Returns:
    A JSON response object and an HTTP status code. The response object contains a 'message' or 
    'error' key depending on the result of the request.
    """
    data = request.get_json()
    email = data.get('email')

    logging.debug("Session Data: %s", session)

    if email is None:
        return jsonify({'error': 'Missing email.'}), 400

    if is_valid_email(email):
        if 'authenticated' in session and session['authenticated']:
            return jsonify({'message': 'Already authenticated.'}), 200

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
        print("Received token:", token)  # Print the received token
        # Decode and verify the JWT token using the app's secret key
        decoded_token = decode_token(token)
        print("Decoded token:", decoded_token)  # Print the decoded token
        email = decoded_token['sub']
        redirect_url = decoded_token['redirect_url']  # Extract the redirect URL from the token

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

if __name__ == '__main__':
    app.run(debug=True)
