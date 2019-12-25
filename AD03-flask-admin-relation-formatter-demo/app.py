from jinja2 import Markup
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView as BaseModelView

db = SQLAlchemy()
admin = Admin(base_template='custom/admin/base.html',
              template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)


####################################################################
# Model

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(128))

    # # for object_ref
    # can_edit = True
    # can_view_details = False


post_tags_table = db.Table(
    'post_tags', db.Model.metadata,
    db.Column('post_id', db.Integer,
              db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tag.id'))
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
        return "{}".format(self.title)

    can_edit = True
    can_view_details = True


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))

    def __str__(self):
        return "{}".format(self.name)


####################################################################
# formatter

def boolean_formatter(val_to_format):
    if val_to_format is None:
        return ''
    if isinstance(val_to_format, bool):
        if val_to_format is True:
            val_to_format = '<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>'
        else:
            val_to_format = '<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>'
    return val_to_format


def _obj_formatter_str(view, context, model,
                       value=None, model_name=None, title=None, fields=None,
                       detail_fields=None, detail_field=None):

    endpoint = model_name

    header, detail_labels, detail_lines = [], [], []
    for k in fields:
        field = {}
        val = getattr(value, str(k['field']))
        field['label'] = k['label']
        field['value'] = str(boolean_formatter(val))
        header.append(field)

    detail_val = getattr(
        value, detail_field) if detail_field is not None else None
    if detail_val is not None and len(detail_val) > 0:
        for detail_key in detail_fields:
            detail_labels.append(detail_key['label'])
        for detail_line_val in detail_val:
            line_vals = []
            for detail_key in detail_fields:
                val = str(boolean_formatter(
                    getattr(detail_line_val, detail_key['field'])))
                line_vals.append(val)
            detail_lines.append(line_vals)
    # 返回 object_ref 引用模板
    return render_template('components/object_ref.html',
                           title=title, value=value, endpoint=endpoint,
                           header=header, detail_labels=detail_labels,
                           detail_lines=detail_lines, view=view)


def _obj_formatter(view, context, model,
                   value=None, model_name=None, title=None, fields=None,
                   detail_fields=None, detail_field=None):
    str_markup = _obj_formatter_str(view, context, model, value, model_name,
                                    title, fields, detail_fields, detail_field)
    return Markup(str_markup)


def _user_obj_formatter(view, context, model, value, *args, **kwargs):
    fields = [
        {
            'label': 'name', 'field': 'name'
        },
        {
            'label': 'username', 'field': 'username'
        }
    ]

    return _obj_formatter(view, context, model,
                          value=value, model_name='user',
                          title=value.username, fields=fields,
                          *args, **kwargs)


def user_formatter(view, context, model, name):
    try:
        s = model.user
    except Exception:
        s = model

    if s is not None:
        return _user_obj_formatter(view, context, model, value=s)
    return ''

####################################################################
# ModelView


class ModelView(BaseModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.model:
            self.model.can_edit = self.can_edit
            self.model.can_view_details = self.can_view_details


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


class PostModelView(ModelView):
    column_list = ('id', 'title', 'date', 'user')

    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        }
    }

    column_formatters = {
        'user': user_formatter
    }

    # for object_ref
    line_fields = [
        {
            'label': 'name',
            'field': 'name'
        },
        {
            'label': 'username',
            'field': 'username'
        }
    ]


admin.add_view(UserModelView(User, db.session))
admin.add_view(PostModelView(Post, db.session))


def initdata(user_count=50, post_count=100):
    import random
    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        user = User(name=f'name{i+1}', username=f'user{i+1}')
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=f'title{i+1}',
            user_id=random.randrange(1, User.query.count())
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


@app.before_first_request
def init_data():
    initdata()


if __name__ == "__main__":
    app.run(debug=True)
