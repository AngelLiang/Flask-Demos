from flask import render_template
from . import app


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


@app.route('/options')
def options():
    return render_template('options.html',
                           bootstrap_table_options=bootstrap_table_options)
