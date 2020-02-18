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


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __str__(self):
        return "{}".format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    category_id = db.Column(db.Integer(), db.ForeignKey(Category.id))
    category = db.relationship(Category, backref='category')

    def __str__(self):
        return "{}".format(self.title)


class CategoryModelView(ModelView):
    column_list = ('id', 'name')


class SiderModelViewMixin(object):

    # 设置列表模板
    list_template = 'admin/model/sider_list.html'

    column_filters = ('category.name',)

    def get_sider_title(self):
        return 'category'

    def get_sider_tree(self):
        return Category.query.all()


class PostModelView(SiderModelViewMixin, ModelView):
    column_list = ('title', 'category', 'date')
    column_default_sort = ('date', True)


admin.add_view(PostModelView(Post, db.session))
admin.add_view(CategoryModelView(Category, db.session))


def initdb(category_count=10, post_count=200):
    import random
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    categories = []
    for i in range(category_count):
        category = Category(
            name=fake.word(),
        )
        categories.append(category)
    db.session.add_all(categories)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            date=fake.past_date(),
            category_id=random.randrange(1, Category.query.count()),
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.before_first_request
def init_data():
    initdb()


if __name__ == "__main__":
    app.run(debug=True)
