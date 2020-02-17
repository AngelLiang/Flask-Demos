from flask import Flask, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_admin.model.template import LinkRowAction
from flask_admin.model.template import EndpointLinkRowAction as _EndpointLinkRowAction

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)

####################################################################
# model


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password

    @property
    def can_view_details(self):
        return self.id != 1

    def can_envelope(self, row_id):
        user = User.query.first()
        return str(user.id) != row_id


####################################################################
# row action


class EndpointLinkRowAction(_EndpointLinkRowAction):
    template_name = 'row_actions.link_row'

    def render(self, context, row_id, row):
        m = self._resolve_symbol(context, self.template_name)
        get_url = self._resolve_symbol(context, 'get_url')

        kwargs = dict(self.url_args) if self.url_args else {}
        kwargs[self.id_arg] = row_id

        url = get_url(self.endpoint, **kwargs)

        return m(self, url, row_id=row_id, row=row)

    def can_show(self, row_id, row):
        return True


class EnvelopeEndpointLinkRowAction(EndpointLinkRowAction):

    def can_show(self, row_id, row):
        return row.can_envelope(row_id)

####################################################################
# view


class ModelView(_ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self.model, 'can_edit'):
            setattr(self.model, 'can_edit', self.can_edit)
        if not hasattr(self.model, 'can_delete'):
            setattr(self.model, 'can_delete', self.can_delete)
        if not hasattr(self.model, 'can_view_details'):
            setattr(self.model, 'can_view_details', self.can_view_details)


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_view_details = True
    can_delete = False

    # 给 flask-admin 每个 row 添加额外的 action
    column_extra_row_actions = [
        EnvelopeEndpointLinkRowAction(
            'glyphicon glyphicon-envelope', '.envelope'),
        # EndpointLinkRowAction('glyphicon glyphicon-envelope', '.envelope'),
        LinkRowAction('glyphicon glyphicon-off', ''),
    ]

    @expose('/user/envelope')
    def envelope(self):
        # TODO:
        row_id = request.args.get('id')
        user = User.query.get(row_id)
        flash(f'envelope to {user.name}')
        return redirect(url_for('.index_view'))


admin.add_view(UserModelView(User, db.session))

####################################################################
# initdb


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
