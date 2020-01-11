from flask import redirect, request, url_for, render_template
from flask_admin import expose
from flask_admin import AdminIndexView as _AdminIndexView
from flask_admin import helpers
from flask_login import current_user, login_user, logout_user


class AdminIndexView(_AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(AdminIndexView, self).index()

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        """handle user login"""
        from .forms import LoginForm

        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        link = '<p>新用户吗？<a href="' + \
            url_for('.register_view') + '">请注册</a>。</p>'

        # self._template_args['form'] = form
        # self._template_args['link'] = link
        # return super(AdminIndexView, self).index()

        return render_template('auth/login.html', form=form, link=link)

    @expose('/register', methods=('GET', 'POST'))
    def register_view(self):
        from .extensions import db
        from .models import User
        from .forms import RegisterForm

        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            user = User()

            form.populate_obj(user)
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            return redirect(url_for('.index'))

        href = url_for('.login_view')
        link = f'<p>已有帐号？请点击<a href="{href}">登录</a>。</p>'
        # self._template_args['form'] = form
        # self._template_args['link'] = link
        # return super(AdminIndexView, self).index()
        return render_template('auth/register.html', form=form, link=link)

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))
