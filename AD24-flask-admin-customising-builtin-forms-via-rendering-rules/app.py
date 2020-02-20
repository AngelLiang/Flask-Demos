from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules

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
    password = db.Column(db.String(128))

    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(128))
    phone = db.Column(db.String(32))
    city = db.Column(db.String(128))
    country = db.Column(db.String(128))
    notes = db.Column(db.Text)


####################################################################
# views


class UserModelView(ModelView):
    can_view_details = True
    can_delete = False
    column_exclude_list = ('password',)
    column_default_sort = 'id'
    column_filters = ('name', 'username',)

    create_template = 'user/create.html'
    edit_template = 'user/edit.html'

    form_create_rules = [
        rules.FieldSet(
            ('username',), 'Account'
        ),
        # Header and four fields. Email field will go above phone field.
        rules.FieldSet(
            ('first_name', 'last_name', 'email', 'phone'), 'Personal'
        ),
        # Separate header and few fields
        rules.Header('Location'),
        rules.Field('city'),
        # String is resolved to form field, so there's no need to explicitly use `rules.Field`
        'country',
        # Show macro that's included in the templates
        rules.Container('rule_demo.wrap', rules.Field('notes'))
    ]
    form_edit_rules = form_create_rules


admin.add_view(UserModelView(User, db.session))

####################################################################
# initdb


def initdb(user_count=50):
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        profile = fake.profile()
        user = User(
            name=profile['name'],
            username=profile['username'],
            first_name=profile['name'].split()[0],
            last_name=profile['name'].split()[1],
            phone=fake.phone_number(),
            email=profile['mail'],
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


if __name__ == "__main__":
    app.run(debug=True)
