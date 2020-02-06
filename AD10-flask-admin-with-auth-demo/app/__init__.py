from flask import Flask
from .extensions import db, login_manager, admin


app = Flask(__name__)
app.config['APP_NAME'] = 'flask-admin-with-auth'
app.config['SECRET_KEY'] = '123456790'

db.init_app(app)
db.app = app
login_manager.init_app(app)
admin.init_app(app)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


def initdb():
    from .models import User
    db.drop_all()
    db.create_all()
    user = User(username='admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()


@app.before_first_request
def before_first_request():
    initdb()
