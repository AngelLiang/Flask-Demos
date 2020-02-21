from flask import Flask
from flask import request
from flask import current_app
from flask import abort
from flask import flash
from flask import url_for
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from wtforms import ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import validate_csrf


db = SQLAlchemy()
csrf = CSRFProtect()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)
csrf.init_app(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    date = db.Column(db.Date)

    def __str__(self):
        return "{}".format(self.title)

    @classmethod
    def from_object(cls, obj):
        return cls(
            title=obj.title,
            text=obj.text
        )


class PostModelView(ModelView):
    can_view_details = True
    column_list = ('id', 'title', 'date')
    column_default_sort = ('date', True)

    details_template = 'admin/model/details_with_action.html'

    def get_model_form_request(self, can_abort=True):
        from flask import g
        from flask_admin.babel import gettext
        from flask_admin.helpers import get_redirect_target
        from flask_admin.model.helpers import get_mdict_item_or_list

        model = getattr(g, 'model', None)
        if model:
            return model

        return_url = get_redirect_target() or self.get_url('.index_view')

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None and can_abort:
            abort(redirect(return_url))

        model = self.get_one(id)

        if model is None and can_abort:
            flash(gettext('Record does not exist.'), 'error')
            abort(redirect(return_url))

        g.model = model
        return model

    def validate_csrf(self):
        model = self.get_model_form_request()
        try:
            csrf_token = request.values.get('csrf_token')
            validate_csrf(csrf_token)
        except ValidationError as e:
            current_app.logger.error(e)
            flash(e.args[0])
            abort(redirect(url_for('.details_view', id=model.id)))

    @expose('/copy-and-create', methods=('POST',))
    def copy_and_create(self):
        """拷贝并创建"""
        self.validate_csrf()
        model = self.get_model_form_request()
        return redirect(url_for('.create_view', id=model.id))

    def create_form(self, obj=None):
        model = self.get_model_form_request()
        return super().create_form(obj=model)


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
