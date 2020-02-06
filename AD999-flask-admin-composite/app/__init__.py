from flask import Flask

from app.extensions import register_extensions
from app.commands import register_commands


def create_app(config=None):
    app = Flask(__name__)
    app.config['APP_NAME'] = 'flask-admin综合示例'
    app.config['SECRET_KEY'] = '123456790'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    register_extensions(app)
    register_commands(app)

    @app.route('/')
    def index():
        return '<a href="/admin/">Click me to go to Admin!</a>'

    return app
