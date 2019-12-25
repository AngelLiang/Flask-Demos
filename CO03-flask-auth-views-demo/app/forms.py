
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField('Usrename', validators=[
                           DataRequired(), Length(1, 80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

    submit = SubmitField('Submit')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(1, 80)])
    password = PasswordField('Password', validators=[DataRequired()])
    comfirm_password = PasswordField(
        'Comfirm Password', validators=[DataRequired()])

    submit = SubmitField('Register')
