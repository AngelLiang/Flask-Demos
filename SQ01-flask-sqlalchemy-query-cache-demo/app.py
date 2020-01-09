from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension

db = SQLAlchemy()
cache = Cache()
toolbar = DebugToolbarExtension()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_PROFILER_ENABLED'] = True

db.init_app(app)
db.app = app
cache.init_app(app)
toolbar.init_app(app)

import cache_query  # noqa
CacheQueryMixin = cache_query.CacheQueryMixin


class User(CacheQueryMixin, db.Model):
    # __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(128))


@app.route('/')
def index():
    return render_template_string('<body></body>')


@app.route('/users')
def users():
    users = User.cache.all()
    users = [user.name for user in users]
    return render_template_string(f'<body>{users}</body>')


@app.route('/users/<user_id>')
def user(user_id=1):
    user = User.cache.get(user_id)
    return render_template_string(f'<body>{user}</body>')


def initdata(user_count=50, post_count=100):
    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        user = User(name=f'name{i+1}', username=f'user{i+1}')
        users.append(user)
    db.session.add_all(users)
    db.session.commit()


@app.before_first_request
def init_data():
    initdata()


if __name__ == "__main__":
    app.run(debug=True)
