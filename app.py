"""
CFIA Louis Backend Flask Application
"""
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/validate_email', methods=['POST'])
def validate_email():
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

    # Regular expression pattern to match valid email addresses
    pattern = r'^[a-zA-Z0-9._%+-]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$'

    if email is None:
        return jsonify({'error': 'No email provided in the request.'}), 400

    if re.match(pattern, email):
        return jsonify({'message': 'Valid email address.'}), 200

    return jsonify({'error': 'Invalid email address.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
