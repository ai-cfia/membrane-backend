"""
CFIA Membrane Backend Flask Application
"""
from app_creator import create_app
from config import AppConfig
from environment_validation import validate_environment_settings

config = AppConfig()
validate_environment_settings(
    config.JWT_CONFIG.client_public_keys_folder,
    config.JWT_CONFIG.server_private_key,
    config.JWT_CONFIG.server_public_key,
    config.MEMBRANE_FRONTEND,
)
app = create_app(config)

if __name__ == "__main__":
    app.run(debug=True)
