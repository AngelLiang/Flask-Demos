from flask import Flask
from app.extensions import db, admin, babel, login_manager


app = Flask(__name__)
app.config['APP_NAME'] = 'flask-admin综合示例'
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from app.extensions import register_extensions
register_extensions(app)


def init_jinja2_functions(app):
    from .utils import is_field_error
    app.add_template_global(is_field_error, 'is_field_error')


init_jinja2_functions(app)

from app.admin.modelviews import *


from app.commands import register_commands
register_commands(app)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'
