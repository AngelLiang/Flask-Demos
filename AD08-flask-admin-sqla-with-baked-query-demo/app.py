from flask import Flask
from sqlalchemy.orm import Session

from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_debugtoolbar import DebugToolbarExtension

import mixin
ModelViewWithBakedQueryMixin = mixin.ModelViewWithBakedQueryMixin
with_baked_query = mixin.with_baked_query


db = SQLAlchemy(session_options={'enable_baked_queries': True})
admin = Admin(template_mode='bootstrap3')
toolbar = DebugToolbarExtension()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG_TB_PROFILER_ENABLED'] = True


db.init_app(app)
db.app = app
admin.init_app(app)
toolbar.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(128))


post_tags_table = db.Table(
    'post_tags', db.Model.metadata,
    db.Column('post_id', db.Integer,
              db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tag.id'))
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='posts')

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __str__(self):
        return "{}".format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return "{}".format(self.name)


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'
    column_searchable_list = ('name',)

    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


class PostModelView(ModelView):
    column_list = ('id', 'title', 'date', 'user')

    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        }
    }


class UserModelViewWithBakedQuery(ModelViewWithBakedQueryMixin, UserModelView):
    pass


@with_baked_query
class PostModelViewWithBakedQuery(PostModelView):
    pass


admin.add_view(UserModelView(User, db.session))
admin.add_view(UserModelViewWithBakedQuery(
    User, db.session,
    name='User With BakedQuery', endpoint='user_with_bakedquery'))

admin.add_view(PostModelView(Post, db.session))
admin.add_view(PostModelViewWithBakedQuery(
    Post, db.session,
    name='Post With BakedQuery', endpoint='post_with_bakedquery'))


def initdata(user_count=50, post_count=100):
    import random
    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        user = User(name=f'name{i+1}', username=f'user{i+1}')
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=f'title{i+1}',
            user_id=random.randrange(1, User.query.count())
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.before_first_request
def init_data():
    initdata()


if __name__ == "__main__":
    app.run(debug=True)
