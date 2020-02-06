import os
import os.path as op

from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['IMAGES_FOLDER_PATH'] = op.join(os.getcwd(), 'images')


from app.extensions import register_extensions, db
register_extensions(app)


def initdb():
    # db.drop_all()
    db.create_all()


@app.before_first_request
def init_data():
    initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'
