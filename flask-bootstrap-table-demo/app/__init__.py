from flask import Flask, render_template

from .extensions import db
from .models import Tree

app = Flask(__name__)
db.init_app(app)
db.app = app

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'
# Create in-memory database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://data.sqlite'


columns = [
    {
        'field': 'id',
        'title': 'Item ID'
    },
    {
        'field': 'name',
        'title': 'Item Name'
    },
    {
        'field': 'price',
        'title': 'Item Price'
    }
]

data = [
    {
        'id': 1,
        'pid': 0,
        'name': 'Item 1',
        'price': '$1',
    },
    {
        'id': 2,
        'pid': 0,
        'name': 'Item 2',
        'price': '$2',
    },
    {
        'id': 3,
        'pid': 1,
        'name': 'Item 3',
        'price': '$2',
    },
    {
        'id': 4,
        'pid': 2,
        'name': 'Item 4',
        'price': '$2',
    },
    {
        'id': 5,
        'pid': 3,
        'name': 'Item 5',
        'price': '$2',
    }
]

bootstrap_table_options = {
    # columns name
    'columns': columns,
    # data
    'data': data,
}


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/tree')
def tree():
    return render_template('tree.html', columns=columns, data=data)


@app.route('/via-js')
def via_js():
    return render_template('via-js.html',
                           bootstrap_table_options=bootstrap_table_options)


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
