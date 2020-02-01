from flask import Flask
from app.extensions import db, admin, babel, login_manager


app = Flask(__name__)
app.config['APP_NAME'] = 'flask-admin综合示例'
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.app = app
babel.init_app(app)
admin.init_app(app)
admin.name = app.config['APP_NAME']
login_manager.init_app(app)


def init_jinja2_functions(app):
    from .utils import is_field_error
    app.add_template_global(is_field_error, 'is_field_error')


init_jinja2_functions(app)

from app.admin.modelviews import *


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


@app.cli.command()
def build():
    """Build sb-admin-2 frontend"""
    import os
    import subprocess

    path = os.path.join(app.root_path, 'static', 'sb-admin-2')
    os.chdir(path)
    subprocess.call(['bower', 'install'], shell=True)


@app.cli.command()
def initdb():
    """Initialize database"""
    from app.fake import fake_admin, initdata

    db.drop_all()
    db.create_all()

    fake_admin()
    initdata()
