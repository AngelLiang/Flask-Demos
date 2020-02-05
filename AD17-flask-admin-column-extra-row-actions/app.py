from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_delete = False

    # 给 flask-admin 每个 row 添加额外的 action
    column_extra_row_actions = [
        EndpointLinkRowAction('glyphicon glyphicon-envelope', '.approve'),
        LinkRowAction('glyphicon glyphicon-off', ''),
    ]

    @expose('/user/approve')
    def approve(self):
        # TODO:
        return redirect(url_for('.index_view'))


admin.add_view(UserModelView(User, db.session))


def initdb(user_count=50):
    db.drop_all()
    db.create_all()

    from faker import Faker
    fake = Faker('zh_CN')

    user = User(username='admin', name='admin')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()

    users = []
    for i in range(user_count):
        user = User(
            name=fake.name(),
            username=fake.profile()['username'],
        )
        user.set_password('123456')
        users.append(user)
    db.session.add_all(users)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


if __name__ == "__main__":
    app.run(debug=True)
