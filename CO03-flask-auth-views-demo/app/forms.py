from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError

from .extensions import db
from .models import User


class CodeMixin(object):
    code = StringField('验证码', validators=[DataRequired()])

    def validate_code(self, field):
        session_code = session.get('code')
        if session_code and session_code.lower() != field.data.lower():
            raise ValidationError('验证码错误')


class LoginForm(CodeMixin, FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')

    def validate_username(self, field):
        user = self.get_user()
        if user is None:
            raise ValidationError('Invalid user')

    def validate_password(self, field):
        user = self.get_user()
        if user and not user.validate_password(self.password.data):
            raise ValidationError('Invalid password')

    def get_user(self):
        if getattr(self, '_user', None):
            return self._user
        self._user = db.session.query(User).filter_by(
            username=self.username.data).first()
        return self._user


class RegisterForm(CodeMixin, FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired()])
    comfirm_password = PasswordField('确认密码', validators=[DataRequired()])

    def validate_username(self, field):
        if db.session.query(User).filter_by(
                username=self.username.data).count() > 0:
            raise ValidationError('Duplicate username')

    def validate_comfirm_password(self, field):
        if self.password.data != self.comfirm_password.data:
            raise ValidationError('两次密码不一致')


def FormFactory(Form, *args, with_code=True, **kwargs):
    form = Form(*args, **kwargs)
    if not with_code:
        del form.code
    return form
