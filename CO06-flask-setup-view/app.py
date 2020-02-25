import string
from wtforms import StringField, PasswordField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_wtf import FlaskForm
from flask import Flask
from flask import request
from flask import flash
from flask import render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
bootstrap = Bootstrap()
admin = Admin(template_mode='bootstrap3')

app = Flask(__name__)
app.config['APP_NAME'] = 'Setup App'
app.config['SECRET_KEY'] = '123456790'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bootstrap.init_app(app)
admin.init_app(app)

####################################################################
# models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    password = db.Column(db.String(128))

    def set_password(self, password):
        self.password = password

    def vertify_password(self, password):
        return self.password == password

####################################################################
# forms


def check_username(word):
    """用户名不能含有特殊符号"""
    invalid_chars = set(string.punctuation.replace('_', ''))

    for ch in word:
        if ch in invalid_chars:
            return False
    return True


class SetupForm(FlaskForm):
    """管理员初始化配置"""
    username = StringField('管理员帐号', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired(), Length(3)])
    comfirm_password = PasswordField(
        '确认密码', validators=[DataRequired(), Length(3)])
    name = StringField('姓名', default='超级管理员')
    email = StringField('邮箱')

    def validate_username(self, field):
        username = self.username.data
        if not check_username(username):
            raise ValidationError('用户名不符合规则')

    def validate_comfirm_password(self, field):
        password = self.password.data
        comfirm_password = self.comfirm_password.data
        if password != comfirm_password:
            raise ValidationError('两次密码不一致')


####################################################################
# views


admin.add_view(ModelView(User, db.session))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    form = SetupForm()
    if request.method == 'POST':
        if form.validate():
            user = User.query.first()
            if user:
                flash('已经有管理员帐号了', category='error')
            else:
                user = User()
                form.populate_obj(user)
                password = form.data['password']
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash('配置管理员成功', category='success')
    return render_template('setup/setup.html', form=form)


@app.route('/')
def index():
    return '<a href="/setup">Click me to setup!</a>'


@app.before_first_request
def init_data():
    db.drop_all()
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
