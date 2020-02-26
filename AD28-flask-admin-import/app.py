import time
import datetime as dt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)

####################################################################
# models


post_tags_table = db.Table(
    'post_tags', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __str__(self):
        return f'{self.name}'


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
    # 导入会出现bug
    # language = db.Column(db.Enum('python', 'flask'))

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __repr__(self):
        return f'{self.title}'


####################################################################
# views

from .import_mixin import ModelViewImportMixin  # noqa


class PostModelView(ModelViewImportMixin, ModelView):

    # column_list = ('title', 'tags', 'date')
    column_exclude_list = ('text',)
    column_labels = {
        'title': '标题',
        'create_date': '创建日期',
        'create_time': '创建时间',
        'update_datetime': '更新时间',
    }

    can_export = True
    column_export_list = (
        'title', 'slug', 'text',
        'price', 'money', 'is_delete', 'create_date', 'create_time',
        'update_datetime',
        'language',
    )
    export_types = ['xls', 'xlsx', 'csv', 'json']
    export_max_rows = 0


admin.add_view(PostModelView(Post, db.session))

####################################################################
# initdb


def initdb(post_count=12, tag_count=3):
    import random
    from faker import Faker

    fake = Faker('zh-CN')

    db.drop_all()
    db.create_all()

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
