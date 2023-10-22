"""
CFIA Membrane Backend Flask Application
"""
from app_creator import create_app
from config import AppConfig

config = AppConfig()
# TODO: env var validation #75
app = create_app(config)

if __name__ == "__main__":
    app.run(debug=True)
