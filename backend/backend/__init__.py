from flask import Flask

from .api import api
from .commands import commands
from .database import db
from .model_json_provider import ModelJsonProvider


def create_app(config="backend.config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config)

    app.json = ModelJsonProvider(app)

    with app.app_context():
        db.init_app(app)
        app.register_blueprint(api)
        app.register_blueprint(commands)

    return app
