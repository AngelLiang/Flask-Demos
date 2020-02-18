from flask import Flask
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin import expose
from flask_admin import BaseView
from flask_admin import AdminIndexView as BaseAdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from flask_httpauth import HTTPBasicAuth


class AdminAuthMixin(object):

    def is_accessible(self):
        _auth = auth.get_auth()
        password = auth.get_auth_password(_auth)
        return auth.authenticate(_auth, password)

    def inaccessible_callback(self, name, **kwargs):
        return auth.auth_error_callback()


class AdminIndexView(AdminAuthMixin, BaseAdminIndexView):

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('index'))


db = SQLAlchemy()
auth = HTTPBasicAuth()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap3', index_view=AdminIndexView())

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
admin.init_app(app)
login_manager.init_app(app)

####################################################################
# model


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password

    def verify_password(self, password):
        return self.password_hash == password


@auth.verify_password
def auth_verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        login_user(user)
        return True
    return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


####################################################################
# form
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length, ValidationError


class UserProfileForm(FlaskForm):
    username = StringField('用户名', render_kw={'readonly': True})
    name = StringField('姓名')

    # email = StringField(_l('个人邮箱'), validators=[Length(max=255)])
    # phone = StringField(_l('手机号码'), validators=[Length(max=32)])


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码')
    new_password = PasswordField('新密码', validators=[DataRequired()])
    new_password_comfirm = PasswordField(
        '新密码确认', validators=[DataRequired()])

    def validate_old_password(self, field):
        password = field.data
        user = current_user
        if not user.verify_password(password):
            raise ValidationError('旧密码错误')

    def validate_new_password_comfirm(self, field):
        new_password_comfirm = field.data
        new_password = self.new_password.data
        if new_password != new_password_comfirm:
            raise ValidationError('两次密码不一致')


####################################################################
# view


from flask import request, current_app, flash


class UserModelView(AdminAuthMixin, ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'


class ProfileView(AdminAuthMixin, BaseView):

    def is_visible(self):
        """不可见但可以访问"""
        return False

    def get_sider_items(self):
        """获取侧边栏items

        :return list: (name, endpotin)
        """
        return [
            ('个人详情', '.profile_view'),
            ('修改密码', '.change_password_view'),
        ]

    @expose('/', methods=('GET', 'POST'))
    def profile_view(self):
        user = User.query.get(current_user.id)
        Form = UserProfileForm
        form = Form(formdata=request.form, obj=user)

        if request.method == 'POST':
            # form = Form(formdata=request.form)
            current_app.logger.debug(form.data)
            if form.validate():
                form.populate_obj(user)
                db.session.add(user)
                db.session.commit()
                flash('更新成功', 'success')
                return redirect(request.url)

        return self.render('profile/profile.html', form=form)

    @expose('/change-password', methods=('GET', 'POST'))
    def change_password_view(self):
        form = ChangePasswordForm(formdata=request.form)
        if request.method == 'POST':
            current_app.logger.debug(form.data)
            if form.validate():
                user = User.query.get(current_user.id)
                user.set_password(form.data['new_password'])
                db.session.add(user)
                db.session.commit()
                flash('密码修改成功，请重新登录', 'success')
                logout_user()
                return redirect(url_for('admin.index'))

        return self.render('profile/change_password.html', form=form)


admin.add_view(UserModelView(User, db.session))
admin.add_view(ProfileView(url='profile'))


def initdb(user_count=50):
    from faker import Faker

    fake = Faker()

    db.drop_all()
    db.create_all()

    user = User(username='admin')
    user.set_password('admin')
    db.session.add(user)

    users = []
    for i in range(user_count):
        profile = fake.simple_profile()
        user = User(
            name=profile['name'],
            username=profile['username'],
        )
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
