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


class PostStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32))
    label = db.Column(db.String(32))

    def __str__(self):
        return f'{self.label}'

    @staticmethod
    def init_data():
        db.session.add_all([
            PostStatus(code='DRIFT', label='drift'),
            PostStatus(code='ISSUED', label='issued'),
        ])


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    status_id = db.Column(db.Integer, db.ForeignKey(PostStatus.id))
    status = db.relationship(PostStatus, foreign_keys=[status_id])

    def __str__(self):
        return f'{self.title}'


def initdb(post_count=100):
    import random
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    PostStatus.init_data()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            date=fake.past_date(),
            status=PostStatus.query.get(
                random.randint(1, PostStatus.query.count())
            )
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


initdb()


####################################################################
# filter
from flask_admin.contrib.sqla.filters import BaseSQLAFilter
from flask_admin.contrib.sqla.filters import FilterEqual
from flask_admin.babel import lazy_gettext


class FilterStatus(BaseSQLAFilter):
    def __init__(self, model, label='label', name=None, options=None, data_type=None):
        options = options or [
            (s.id, getattr(s, label)) for s in model.query.all()
        ]
        self.name = name or 'Status'
        super().__init__(model.id, self.name, options=options, data_type=data_type)

    def apply(self, query, value, alias=None):
        return query.filter(self.column == value)

    def operation(self):
        return lazy_gettext('equals')


####################################################################
# views

class PostModelView(ModelView):
    can_view_details = True
    column_list = ('id', 'title', 'status', 'date',)
    column_default_sort = ('date', True)

    column_filters = [
        FilterStatus(PostStatus)
    ]


admin.add_view(PostModelView(Post, db.session))


# @app.before_first_request
# def init_data():
#     initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == "__main__":
    app.run(debug=True)
