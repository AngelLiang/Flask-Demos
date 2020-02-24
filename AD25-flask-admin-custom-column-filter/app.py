from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db.app = app
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
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return f'{self.name}'


class PostStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32))
    label = db.Column(db.String(32))

    def __str__(self):
        return f'{self.label}'

    @staticmethod
    def init_data():
        db.session.add_all([
            PostStatus(code='DRAFT', label='draft'),
            PostStatus(code='ISSUED', label='issued'),
        ])


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    status_id = db.Column(db.Integer, db.ForeignKey(PostStatus.id))
    status = db.relationship(PostStatus, foreign_keys=[status_id])

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __str__(self):
        return f'{self.title}'


####################################################################
# views


def enum_filters_factory(column, label, options):
    from flask_admin.contrib.sqla.filters import (
        EnumEqualFilter, EnumFilterNotEqual,
        EnumFilterEmpty, EnumFilterInList,
        EnumFilterNotInList
    )
    return [
        EnumEqualFilter(column, label, options=options),
        EnumFilterNotEqual(column, label, options=options),
        EnumFilterInList(column, label, options=options),
        EnumFilterNotInList(column, label, options=options),
        EnumFilterEmpty(column, label, options=options),
    ]


def generate_column_filters():
    from sqlalchemy.exc import OperationalError

    try:
        column_filters = []

        column = PostStatus.id
        options = db.session.query(
            PostStatus.id, PostStatus.label
        ).all()
        column_filters.extend(
            enum_filters_factory(column, 'Status', options=options)
        )
        return column_filters
    except OperationalError:
        return []


class PostModelView(ModelView):
    can_view_details = True
    column_list = ('id', 'title', 'status', 'tags', 'date',)
    column_default_sort = ('date', True)

    column_filters = generate_column_filters()+['tags']


class PostStatusModelView(ModelView):
    can_create = False
    can_delete = False


class TagModelView(ModelView):
    pass


admin.add_view(PostModelView(Post, db.session))
admin.add_view(PostStatusModelView(PostStatus, db.session))
admin.add_view(TagModelView(Tag, db.session))


####################################################################
# initdb


def initdb(post_count=500, tag_count=50):
    import random
    from faker import Faker

    fake = Faker()

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

    PostStatus.init_data()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            date=fake.past_date(),
            status=PostStatus.query.get(
                random.randint(1, PostStatus.query.count())
            ),
            tags=list(set([
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count()))
            ]))
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
