from flask import Flask

from .extensions import db
from .models import Tree

app = Flask(__name__)
db.init_app(app)
db.app = app

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
# Create in-memory database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://data.sqlite'

from .views import *  # noqa


def initdata(count=10):
    db.drop_all()
    db.create_all()

    trunk = Tree(name="Trunk")
    db.session.add(trunk)
    for i in range(count):
        branch = Tree()
        branch.name = "Branch " + str(i+1)
        branch.parent = trunk
        db.session.add(branch)
        for j in range(5):
            leaf = Tree()
            leaf.name = "Leaf " + str(j+1)
            leaf.parent = branch
            db.session.add(leaf)
            for k in range(3):
                item = Tree()
                item.name = "Item " + str(k+1)
                item.parent = leaf
                db.session.add(item)
    db.session.commit()


@app.before_first_request
def init_data():
    initdata()
