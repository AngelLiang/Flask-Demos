from flask import Flask
from app.extensions import db, admin, admin_backup


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.app = app
admin.init_app(app)
admin_backup.init_app(app, db)


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


from app.models import User, Post, Tag
from app.admin.views import *
admin_backup.add_file_view(admin)


def initdata():
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

    user = User(username='admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()

    users = []
    for i in range(20):
        user = User(name=fake.name())
        users.append(user)
    db.session.add_all(users)
    db.session.commit()


@app.before_first_request
def before_first_request():
    initdata()
