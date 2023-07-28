"""Application factory module"""
from flask import Flask
from flask_cors import CORS

from config import config
from app.extensions import swagger
from app.api import api_bp


def create_app(config_name) -> Flask:
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(config_name)

    # Register blueprint for api.
    app.register_blueprint(api_bp)

    swagger.init_app(app)
    CORS(app)  # For handling Cross Origin Resource Sharing in Swagger UI

    return app

