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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    def __repr__(self):
        return f'{self.title}'


####################################################################
# views


class PostModelView(ModelView):

    can_export = True

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
