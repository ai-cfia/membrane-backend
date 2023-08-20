from flask import jsonify
from jwt_utils import (JWTError, SessionError, JWTAppIdMissingError, JWTPublicKeyNotFoundError)
from request_helpers import (EmailError, InvalidTokenError, MissingTokenError)

def register_error_handlers(app):

    # Error handlers
    @app.errorhandler(JWTAppIdMissingError)
    def handle_jwt_app_id_missing_error(_error):
        """Handle missing app_id in JWT."""
        return jsonify("Error: The JWT is missing an app_id."), 400

    @app.errorhandler(JWTPublicKeyNotFoundError)
    def handle_jwt_public_key_not_found_error(_error):
        """Handle missing public key for a given JWT app_id."""
        return jsonify("Error: The public key corresponding to the JWT's app_id was not found."), 400

    @app.errorhandler(JWTError)
    def handle_jwt_error(error):
        """Handle generic JWT-related errors."""
        return jsonify(str(error)), 400

    @app.errorhandler(EmailError)
    def handle_email_error(error):
        """Handle email-related errors."""
        return jsonify(str(error)), 400

    @app.errorhandler(SessionError)
    def handle_session_error(error):
        """Handle session-related errors."""
        return jsonify(str(error)), 400

    @app.errorhandler(MissingTokenError)
    def handle_missing_token_error(error):
        return jsonify({'error': str(error)}), 400

    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token_error(error):
        return jsonify({'error': str(error)}), 400
