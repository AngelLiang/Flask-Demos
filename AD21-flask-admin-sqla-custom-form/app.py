from flask import Flask
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
# model


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    def __str__(self):
        return "{}".format(self.title)

####################################################################
# form


from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.fields.html5 import DateField
# from flask_admin.form.fields import DateTimeField


class PostForm(FlaskForm):
    title = StringField()
    text = TextAreaField()
    date = DateField()


####################################################################
# view


class PostModelView(ModelView):
    column_list = ('id', 'title', 'date')
    column_default_sort = ('date', True)

    # custom form
    form = PostForm


admin.add_view(PostModelView(Post, db.session))


def initdb(post_count=100):
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            date=fake.past_date(),
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
