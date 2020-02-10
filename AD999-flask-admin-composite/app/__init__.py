from flask import Flask

from app.settings import config
from app.extensions import register_extensions
from app.commands import register_commands


def create_app(config=config['default']):
    app = Flask(__name__)

    app.config.from_object(config)
    config.init_app(app)

    register_extensions(app)
    register_commands(app)

    @app.route('/')
    def index():
        return '<a href="/admin/">Click me to go to Admin!</a>'

    return app
