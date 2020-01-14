
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError

from .extensions import db
from .models import User


class LoginForm(FlaskForm):
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
        self._user = db.session.query(User).filter_by(
            username=self.username.data).first()
        return self._user


class RegisterForm(FlaskForm):
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
