"""
This module contains initialization logic for the Flask application
"""
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

from flask import Flask
from flask_cors import CORS
from config import Config
from website.core import bp as core_bp

import datetime

def create_app(config_object=Config):
    app = Flask(__name__)
    app.permanent_session_lifetime = datetime.timedelta(minutes=10)
    app.config.from_object(config_object)
    CORS(app, origins="http://localhost:8080", supports_credentials=True)
    app.logger.info("Registering blueprint %s", core_bp.name)
    app.register_blueprint(core_bp)
    return app
 
