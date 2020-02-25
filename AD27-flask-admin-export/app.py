from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
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
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __repr__(self):
        return f'{self.title}'


####################################################################
# views


class PostModelView(ModelView):

    column_list = ('title', 'tags', 'date')

    can_export = True
    column_export_list = ('id', 'title', 'tags', 'text', 'date')
    """
        Collection of the field names included in the export.
        If set to `None`, will get them from the model.
    """

    column_export_exclude_list = None
    """
        Collection of fields excluded from the export.
    """

    column_formatters_export = None
    """
        Dictionary of list view column formatters to be used for export.

        Defaults to column_formatters when set to None.

        Functions the same way as column_formatters except
        that macros are not supported.
    """

    column_type_formatters_export = None
    """
        Dictionary of value type formatters to be used in the export.

        By default, two types are formatted:

        1. ``None`` will be displayed as an empty string
        2. ``list`` will be joined using ', '

        Functions the same way as column_type_formatters.
    """

    # 使用 xls 或 xlsx 还需安装 openpyxl
    # `pip install tablib[xls,xlsx]` or `pip install openpyxl`
    export_types = ['xls', 'xlsx', 'csv', 'json']
    """
        A list of available export filetypes. `csv` only is default, but any
        filetypes supported by tablib can be used.

        Check tablib for https://github.com/kennethreitz/tablib/blob/master/README.rst
        for supported types.
    """

    # 允许导出的最大行数，默认是不限制，如果设置为 `None` 则使用 `page_size`
    export_max_rows = 0


admin.add_view(PostModelView(Post, db.session))

####################################################################
# initdb


def initdb(post_count=100, tag_count=10):
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

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            date=fake.past_date(),
            tags=list(set([
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count())),
                Tag.query.get(random.randint(1, Tag.query.count())),
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
