import datetime as dt
from sqlalchemy import desc

from flask import Flask, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, expose
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, current_user
from flask_bootstrap import Bootstrap

from forms import MessageForm

db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap3')
bootstrap = Bootstrap()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'

db.init_app(app)
db.app = app
admin.init_app(app)
login_manager.init_app(app)
bootstrap.init_app(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))

    def set_password(self, passowrd):
        self.password_hash = passowrd

    messages_sent = db.relationship(
        'Message',
        foreign_keys='Message.sender_id',
        backref='sender', lazy='dynamic')
    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.recipient_id',
        backref='recipient', lazy='dynamic')

    def new_messages(self):
        messages = Message.query.filter_by(recipient=self, is_read=False).order_by(
            desc(Message.created_at)).all()
        for message in messages:
            setattr(message, 'url', url_for(
                'message.details_view', id=message.id))
        return messages


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))

    is_read = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime, index=True, default=dt.datetime.now)

    def __repr__(self):
        return f'<Message {self.body}>'


class MessagesMixin(object):

    @property
    def messages(self):
        messages = Message.query.filter_by(
            recipient=current_user, is_read=False).order_by(
            desc(Message.created_at)).all()
        for message in messages:
            setattr(message, 'url', url_for(
                'message.details_view', id=message.id))
        return messages


class BaseModelView(MessagesMixin, ModelView):
    pass


class UserModelView(BaseModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_delete = False

    column_extra_row_actions = [
        # LinkRowAction('glyphicon glyphicon-off', 'http://localhost/?id={row_id}'),
        EndpointLinkRowAction(
            'glyphicon glyphicon-envelope', '.send_message')
    ]

    @expose('/send-message', methods=['GET', 'POST'])
    def send_message(self):
        id = request.args.get('id')
        recipient = User.query.get(id)
        if recipient is None:
            flash('user_id is error.', 'error')
            return redirect(url_for('.index_view'))
        form = MessageForm()
        if form.validate_on_submit():
            msg = Message(sender=current_user,
                          recipient=recipient,
                          body=form.message.data)
            db.session.add(msg)
            db.session.commit()
            flash(f'Your message has been sent to {recipient.name or recipient.username}')
            return redirect(url_for('.index_view'))
        return self.render('/send_message.html', form=form, recipient=recipient)


class MessageModelView(BaseModelView):
    column_list = ('sender.name', 'recipient.name',
                   'body', 'is_read', 'created_at')
    column_default_sort = ('created_at', True)

    can_view_details = True
    can_edit = False
    can_delete = False


admin.add_view(UserModelView(User, db.session))
admin.add_view(MessageModelView(Message, db.session))


@app.route('/')
def index():
    return '<a href="/admin/">Click me to go to Admin!</a>'


def initdb(user_count=50, message_count=100):
    import random
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

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
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    messages = []
    for i in range(message_count):
        message = Message(
            sender_id=random.randrange(1, User.query.count()),
            recipient_id=random.randrange(1, User.query.count()),
            body=fake.sentence(),
            created_at=fake.date_time_between(start_date='-35d')
        )
        messages.append(message)
    db.session.add_all(messages)
    db.session.commit()


@app.before_first_request
def init_data():
    initdb()


@app.cli.command()
def build():
    """Build sb-admin-2 frontend"""
    import os
    import subprocess

    path = os.path.join(app.root_path, 'static', 'sb-admin-2')
    os.chdir(path)
    subprocess.call(['bower', 'install'], shell=True)


if __name__ == "__main__":
    app.run(debug=True)
