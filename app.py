"""
CFIA Louis Backend Flask Application
"""
import logging
import jwt
from flask import Flask, request, jsonify, session, make_response
from flask_session import Session
from utils import is_valid_email, create_jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET'
app.config['SESSION_TYPE'] = 'filesystem'  # Use file-based session storage (you can explore other storage options)
Session(app)

@app.route('/login', methods=['POST'])
def login():
    """
    Validates an email address received in the request JSON data.

    - The function expects a JSON object with an 'email' field containing the email address
      to validate.
    - It checks if the email is valid and ends with one of the allowed domains (gc.ca, canada.ca,
      or inspection.gc.ca).

    Returns:
        - If the email is valid, returns a JSON response with 'message': 'Valid email address.'
          and status code 200.
        - If the email is invalid or missing in the request, returns a JSON response with
          'error': 'Invalid email address.' and status code 400.
    """
    # Get the email address from the request JSON data
    data = request.get_json()
    email = data.get('email')

    if email is None:
        return jsonify({'error': 'No email provided in the request.'}), 400

    if is_valid_email(email):
        jwt_token = create_jwt(email)  # Using the create_jwt function from utils.py

        if 'authenticated' in session and session['authenticated']:
            # If the user is already authenticated, return the JWT in the response body
            return jsonify({'message': 'Valid email address.', 'jwt': jwt_token}), 200

        # If the user is not authenticated, send a JWT link to the email
        # (code for sending email is not implemented)
        # SendEmailWithJWT(email)  # Implement this function to send an email with the JWT link

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        return jsonify({'message': 'Valid email address. Email sent with JWT link.', 'jwt': jwt_token}), 200

    return jsonify({'error': 'Invalid email address.'}), 400



@app.route('/verify_token/<token>', methods=['GET'])
def verify_token(token):
    """
    Handle the verification of the JWT token received via the link.

    Parameters:
        token (str): The JWT token extracted from the URL.

    Returns:
        - If the token is valid and not expired, set the session variables
          'authenticated' and 'user_email' and redirect the user to the dashboard.
        - If the token is expired or invalid, return a JSON response with an error message.
    """
    try:
        print("Received token:", token)  # Print the received token
        # Decode and verify the JWT token using the app's secret key
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        print("Decoded token:", decoded_token)  # Print the decoded token
        email = decoded_token['email']

        # Set the 'authenticated' key in the session dictionary to indicate that the user is authenticated
        session['authenticated'] = True
        session['user_email'] = email

        # Redirect the user to a dashboard or a welcome page
        return make_response('Email Verified', 200)

    except jwt.ExpiredSignatureError:
        # Handle the case where the token is expired
        return jsonify({'error': 'Token has expired.'}), 400
    except jwt.InvalidTokenError as invalid_token_error:
        # Log the exception message to inspect the reason for the decoding failure
        logging.error('JWT Token decoding error: %s', invalid_token_error)
        return jsonify({'error': 'Invalid token.'}), 400


if __name__ == '__main__':
    app.run(debug=True)
