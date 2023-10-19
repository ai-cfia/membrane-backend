from flask import jsonify


# pylint: disable=unused-variable
def register_error_handlers(app):
    """Error handlers"""

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle all unexpected errors."""
        app.logger.exception(f"Unexpected error occurred: {error}")
        generic_error_field = app.config["MEMBRANE_GENERIC_500_ERROR_FIELD"]
        generic_error = app.config["MEMBRANE_GENERIC_500_ERROR"]
        return jsonify({generic_error_field: generic_error}), 500
