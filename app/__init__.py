import os
from flask import Flask
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    app = Flask(__name__, instance_relative_config=False)

    # Configuración de API key desde variable de entorno
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')

    from .routes import main
    app.register_blueprint(main)

    return app
