import datetime as dt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader


db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)

####################################################################
# models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(128))


post_tags_table = db.Table(
    'post_tags', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    slug = db.Column(db.String(1024))
    text = db.Column(db.Text)
    price = db.Column(db.Float)
    is_delete = db.Column(db.Boolean)
    create_date = db.Column(db.Date)
    create_time = db.Column(db.Time)
    update_datetime = db.Column(db.DateTime, onupdate=dt.datetime.now)
    money = db.Column(db.DECIMAL(10, 4))
    language = db.Column(db.Enum('python', 'flask'))

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='posts')

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __str__(self):
        return "{}".format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return f'{self.name}'

####################################################################
# views


class UserQueryAjaxModelLoader(QueryAjaxModelLoader):
    def format(self, model):
        if not model:
            return None
        return (str(model.id), f'{model.name} <{model.username}>')


class UserModelView(ModelView):
    can_delete = False
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'
    column_filters = ('name', 'username',)

    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


class PostModelView(ModelView):
    can_view_details = True
    column_list = (
        'title', 'slug', 'text', 'tags',
        'price', 'money', 'is_delete', 'create_date', 'create_time',
        'update_datetime',
        'language',
        'user',
    )
    column_exclude_list = ('text',)
    column_default_sort = ('create_date', True)

    form_ajax_refs = {
        # 'user': {
        #     'fields': (User.name, User.username),
        #     'placeholder': 'Please input name or username',
        #     'page_size': 10,
        #     'minimum_input_length': 0,
        # }
        'user': UserQueryAjaxModelLoader(
            'user', db.session, User,
            placeholder='Please input name or username',
            fields=(User.name, User.username),
            page_size=20,
            minimum_input_length=0,
        )
    }


admin.add_view(UserModelView(User, db.session))
admin.add_view(PostModelView(Post, db.session))

####################################################################
# initdb


def initdb(user_count=50, post_count=100, tag_count=10):
    import random
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        profile = fake.simple_profile()
        user = User(
            name=profile['name'],
            username=profile['username'],
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    tags = []
    for i in range(tag_count):
        tag = Tag(
            name=fake.word(),
        )
        tags.append(tag)
    db.session.add_all(tags)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            slug=fake.sentence(),
            text=fake.text(),
            tags=list(set([
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count())),
            ])),
            money=fake.pydecimal(),
            price=fake.pyfloat(),
            is_delete=random.choice((False, True)),
            create_date=fake.past_date(),
            create_time=fake.time_object(),
            update_datetime=fake.past_datetime(),
            user=User.query.get(random.randint(1, User.query.count())),
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == "__main__":
    app.run(debug=True)
