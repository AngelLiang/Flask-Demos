from flask import render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

from . import app
from .extensions import db
from .models import User
from .forms import LoginForm, RegisterForm


@app.route('/')
@login_required
def index():
    return f'<div>hello {current_user.username}, <a href="/auth/logout">logout</a></div>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    redirect_url = request.args.get('next') or url_for('index')
    if current_user.is_authenticated:
        return redirect(redirect_url)

    form = LoginForm()

    if request.method == 'POST' and form.validate():
        username = form.data['username']
        password = form.data['password']
        remember_me = form.data['remember_me']

        # TODO:
        user = User.query.filter_by(username=username).first()

        if user is not None and user.validate_password(password):
            login_user(user, remember=remember_me)
            return redirect(redirect_url)
        flash('用户名或密码错误', 'error')
    return render_template('auth/login.html', form=form)


@app.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('登出成功', 'success')
    return redirect(url_for('login'))


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    """注册"""
    if current_app.config.get('REGISTER_ENABLE') is False:
        abort(404)

    form = RegisterForm()

    if request.method == 'POST' and form.validate():
        username = form.data['username']
        password = form.data['password']

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            current_app.logger.error(e)
            flash('用户注册发生错误')
        # 注册后自动登录
        login_user(user)
        return redirect(url_for('index'))

    return render_template('auth/register.html', form=form)
