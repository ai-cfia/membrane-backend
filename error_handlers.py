from quart import jsonify

# pylint: disable=unused-variable
def register_error_handlers(app):
    """Error handlers"""

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        """Handle all unexpected errors."""
        app.logger.error(f"Unexpected error occurred: {str(error)}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
