from sqlalchemy.exc import IntegrityError
from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import current_user, login_user, logout_user, login_required
from wtforms.validators import ValidationError

from . import app
from .extensions import db
from .models import User
from .forms import LoginForm, RegisterForm


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
        return redirect(redirect_url)

    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        # remember: https://flask-login.readthedocs.io/en/latest/#remember-me
        login_user(user, remember=form.remember_me.data)
        return redirect(redirect_url)

    if current_app.config.get('AUTH_REGISTER_ENABLE'):
        href = url_for('register')
        register_link = f'<p>新用户吗？<a href="{href}">请注册</a>。</p>'
    else:
        register_link = None
    return render_template('auth/login.html', form=form, register_link=register_link)


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
        abort(404)

    form = RegisterForm()
    if request.method == 'POST' and form.validate():
        user = User()

        form.populate_obj(user)
        user.set_password(form.password.data)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            current_app.logger.error(e)
            flash('用户注册发生错误')

        # 注册后自动登录
        if current_app.config.get('AUTH_REGISTER_AFTER_LOGIN'):
            login_user(user)
        return redirect(url_for('index'))

    href = url_for('login')
    login_link = f'<p>已有帐号？请点击<a href="{href}">登录</a>。</p>'
    return render_template('auth/register.html', form=form, login_link=login_link)
