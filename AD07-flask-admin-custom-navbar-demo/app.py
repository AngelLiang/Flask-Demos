from flask import Flask
from flask_admin import Admin, AdminIndexView
from flask_admin.base import MenuLink
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3', index_view=AdminIndexView(
    menu_icon_type='glyph', menu_icon_value='glyphicon-home')
)

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)


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
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))
    user = db.relationship(User, backref='posts')

    tags = db.relationship('Tag', secondary=post_tags_table)

    def __str__(self):
        return '{}'.format(self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return '{}'.format(self.name)


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_delete = False
    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


class PostModelView(ModelView):
    column_list = ('title', 'date', 'user')
    column_default_sort = ('date', True)

    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        }
    }


def admin_add_category(admin, target_category, *args, **kwargs):
    """
    :param admin: flask-admin 实例
    :param target_category: str, 分类名称

    Usage::

        category = 'category'
        admin_add_category(admin, category)
        admin.add_sub_category('user', category)
        admin.add_view(ShareUserModelView(
            User, db.session, name='user', category='user'))

    """
    from flask_admin.menu import MenuCategory

    cat_text = target_category.decode('utf-8')\
        if isinstance(target_category, bytes) else target_category
    category = admin._menu_categories.get(cat_text)
    if category is None:
        category = MenuCategory(target_category)
        category.class_name = admin.category_icon_classes.get(cat_text)
        admin._menu_categories[cat_text] = category
        admin._menu.append(category)
        return True


admin.add_view(UserModelView(
    User, db.session, category='Account',
    menu_icon_type='glyph', menu_icon_value='glyphicon-user'))
admin.add_view(PostModelView(
    Post, db.session, category='Account',
    menu_icon_type='glyph', menu_icon_value='glyphicon-edit'))

admin_add_category(admin, 'Other')
admin.add_sub_category(name='Links', parent_name='Other')
admin.add_link(MenuLink(name='Back Home', url='/admin', category='Other'))
admin.add_link(MenuLink(name='Flask-Demos',
                        url='https://github.com/AngelLiang/Flask-Demos',
                        category='Links'))
admin.add_link(MenuLink(
    name='Baidu', url='http://www.baidu.com/', category='Links'))

# 添加到banav的右上角
admin.add_links(MenuLink(name='Logout', url='/'))


def initdata(user_count=50, post_count=100):
    import random
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        profile = fake.profile()
        user = User(name=profile['name'], username=profile['username'])
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            user_id=random.randrange(1, User.query.count()),
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
