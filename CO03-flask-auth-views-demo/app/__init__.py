from flask import Flask
from .extensions import db, login_manager


app = Flask(__name__)
app.config['APP_NAME'] = 'Auth Demo'
app.config['SECRET_KEY'] = '123456790'
app.config['AUTH_REGISTER_ENABLE'] = True
app.config['AUTH_REGISTER_AFTER_LOGIN'] = True

db.init_app(app)
db.app = app
login_manager.init_app(app)


def init_jinja2_functions(app):
    from .utils import is_field_error
    app.add_template_global(is_field_error, 'is_field_error')


init_jinja2_functions(app)

from .views import *  # noqa


def initdata():
    from .models import User
    db.drop_all()
    db.create_all()
    user = User(username='admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()


@app.before_first_request
def before_first_request():
    initdata()
