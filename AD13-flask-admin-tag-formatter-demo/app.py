from jinja2 import Markup
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)


####################################################################
# Model


posts_tags_table = db.Table(
    'posts_tags', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    tags = db.relationship('Tag', secondary=posts_tags_table)

    def __str__(self):
        return f"{self.title}"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return f"{self.name}"


####################################################################
# formatter

def tags_formatter(view, context, model, name):
    tags = getattr(model, name, [])
    if not tags:
        return ''
    tags_templates = []
    for tag in tags:
        name = tag.name
        template_string = f'<span style="display: inline-block;" class="label label-primary">{name}</span>'
        tags_templates.append(render_template_string(template_string))
    return Markup(' '.join(tags_templates))

####################################################################
# ModelView


class PostModelView(ModelView):
    column_list = ('id', 'title', 'tags', 'date')

    column_formatters = {
        'tags': tags_formatter
    }


admin.add_view(PostModelView(Post, db.session))


def initdata(user_count=50, post_count=100, tag_count=20):
    import random
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

    tags = []
    for i in range(tag_count):
        tag = Tag(name=fake.word())
        tags.append(tag)
    db.session.add_all(tags)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            tags=list(set([
                Tag.query.get(random.randrange(1, Tag.query.count())),
                Tag.query.get(random.randrange(1, Tag.query.count())),
                Tag.query.get(random.randrange(1, Tag.query.count()))
            ])),
            date=fake.past_date()
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


@app.before_first_request
def init_data():
    initdata()


if __name__ == "__main__":
    app.run(debug=True)
