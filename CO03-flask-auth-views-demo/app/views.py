from sqlalchemy.exc import IntegrityError
from flask import (
    flash,
    url_for,
    request,
    redirect,
    current_app,
    render_template,
    abort,
    session
)
from flask_login import current_user, login_user, logout_user, login_required

from . import app
from .extensions import db
from .models import User
from .forms import LoginForm, RegisterForm, FormFactory


LOGIN_ERROR_KEY = 'login_error_count'


def login_error_clear(key=LOGIN_ERROR_KEY):
    if key in session:
        del session[key]


def login_error_increase(key=LOGIN_ERROR_KEY):
    if key in session:
        session[key] += 1
    else:
        session[key] = 1


def is_login_error_exceed(key=LOGIN_ERROR_KEY):
    return session.get(key, 0) >= \
        current_app.config.get('AUTH_LOGIN_WITH_CODE_AFTER_X_ERRORS', 0)


@app.route('/')
@app.route('/index')
@login_required
def index():
    href = url_for('logout')
    return f'<div>hello {current_user.username}, <a href="{href}">logout</a></div>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    redirect_url = request.args.get('next') or url_for('index')
    if current_user.is_authenticated:
        # 已经登录了
        return redirect(redirect_url)

    # form = LoginForm()
    if current_app.config.get('AUTH_LOGIN_WITH_CODE') and is_login_error_exceed():
        # if current_app.config.get('AUTH_LOGIN_WITH_CODE'):
        form = FormFactory(LoginForm, with_code=True)
        verify_code_url = url_for('get_code')
    else:
        form = FormFactory(LoginForm, with_code=False)
        verify_code_url = None

    if request.method == 'POST':
        if form.validate():
            # 登录成功
            user = form.get_user()
            # remember: https://flask-login.readthedocs.io/en/latest/#remember-me
            login_user(user, remember=form.remember_me.data)
            login_error_clear()  # 清除登录失败次数
            return redirect(redirect_url)
        else:
            # 登录失败
            login_error_increase()  # 登入失败次数加一
            if current_app.config.get('AUTH_LOGIN_WITH_CODE') and is_login_error_exceed():
                new_form = FormFactory(LoginForm, with_code=True)
                new_form.username.errors = form.username.errors
                new_form.password.errors = form.password.errors
                code = getattr(form, 'code', None)
                if code:
                    new_form.code.errors = form.code.errors
                form = new_form
                verify_code_url = url_for('get_code')

    if current_app.config.get('AUTH_REGISTER_ENABLE'):
        href = url_for('register')
        register_link = f'<p>新用户吗？请<a href="{href}">注册</a>。</p>'
    else:
        register_link = None
    return render_template('auth/login.html',
                           form=form,
                           register_link=register_link,
                           verify_code_url=verify_code_url)


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('登出成功', 'success')
    return redirect(url_for('login'))


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if not current_app.config.get('AUTH_REGISTER_ENABLE'):
        # 没有启用注册功能
        abort(404)

    # form = RegisterForm()
    if current_app.config.get('AUTH_REGISTER_WITH_CODE'):
        form = FormFactory(RegisterForm, with_code=True)
        verify_code_url = url_for('get_code')
    else:
        form = FormFactory(RegisterForm, with_code=False)
        verify_code_url = None

    if request.method == 'POST' and form.validate():
        # 表单校验成功
        user = User()

        form.populate_obj(user)
        user.set_password(form.password.data)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            current_app.logger.error(e)
            flash('用户注册发生错误')

        if current_app.config.get('AUTH_REGISTER_AFTER_LOGIN'):
            # 注册成功后自动登录
            login_user(user)
        return redirect(url_for('index'))

    href = url_for('login')
    login_link = f'<p>已有帐号？请点击<a href="{href}">登录</a>。</p>'
    verify_code_url = url_for('get_code')
    return render_template('auth/register.html',
                           form=form,
                           login_link=login_link,
                           verify_code_url=verify_code_url)


@app.route('/auth/code')
def get_code():
    from app.verify_code import generate_flask_response
    return generate_flask_response()
