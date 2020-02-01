from flask import redirect, request, url_for, render_template
from flask_admin import expose
from flask_admin import AdminIndexView as _AdminIndexView
from flask_admin import helpers
from flask_login import current_user, login_user, logout_user

from app.models import User, Post, Tag, Comment
from app.utils.stats_utils import get_stats_by_week


def get_post_week_stats(past=1, *args, **kwargs):
    return get_stats_by_week(Post.created_at, past, *args, **kwargs)


def stats2data(stats):
    data = [
        {'period': stat[0].strftime('%Y-%m-%d'), 'count': stat[1]}
        for stat in stats
    ]
    return data


class AdminIndexView(_AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        user_total = User.query.count()
        post_total = Post.query.count()
        comment_total = Comment.query.count()
        tag_total = Tag.query.count()

        past = request.args.get('past', type=int, default=0)
        stats = get_post_week_stats(past)
        post_stats = stats2data(stats)

        if past == 1:
            stats_title = '上周文章发表数量'
        else:
            stats_title = '本周文章发表数量'

        return self.render('admin/dashboard.html',
                           user_total=user_total,
                           post_total=post_total,
                           comment_total=comment_total,
                           tag_total=tag_total,
                           post_stats=post_stats,
                           stats_title=stats_title)

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
        return render_template('auth/login.html', form=form, link=link)

    @expose('/register', methods=('GET', 'POST'))
    def register_view(self):
        from app.extensions import db
        from app.models import User
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
        return render_template('auth/register.html', form=form, link=link)

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))
