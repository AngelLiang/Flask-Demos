from flask import redirect, request, url_for, render_template
from flask_admin import expose
from flask_admin import AdminIndexView as _AdminIndexView
from flask_admin import helpers
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.models import User, Post, Tag, Comment
from app.utils.stats_utils import get_stats_by_days, get_stats_by_week, get_stats_by_month, get_stats_by_year
from .mixins import AlertsMixin


def get_post_week_stats(weeks=0):
    return get_stats_by_week(db.session, Post.created_at, weeks)


def get_post_past_day_stats(days=0):
    return get_stats_by_days(db.session, Post.created_at, days)


def get_post_month_status(months=0):
    return get_stats_by_month(db.session, Post.created_at, months)


def get_post_year_status(years=0, sep='day'):
    return get_stats_by_year(db.session, Post.created_at, years, sep)


def stats2data(stats):
    data = [
        {'period': stat[0].strftime('%Y-%m-%d'), 'count': stat[1]}
        for stat in stats
    ]
    return data


class AdminIndexView(AlertsMixin, _AdminIndexView):

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view', next=request.url))

        user_total = User.query.count()
        post_total = Post.query.count()
        comment_total = Comment.query.count()
        tag_total = Tag.query.count()

        stats_actions = {
            'this-week': ('本周文章发表数量', url_for('admin.index', stats='this-week'), lambda: get_post_week_stats(0)),
            'last-week': ('上周文章发表数量', url_for('admin.index', stats='last-week'), lambda: get_post_week_stats(-1)),
            'this-month': ('本月文章发表数量', url_for('admin.index', stats='this-month'), lambda: get_post_month_status(0)),
            'last-month': ('上月文章发表数量', url_for('admin.index', stats='last-month'), lambda: get_post_month_status(-1)),
            'past-7-days': ('过去7天文章发表数量', url_for('admin.index', stats='past-7-days'), lambda: get_post_past_day_stats(-7)),
            'past-14-days': ('过去14天文章发表数量', url_for('admin.index', stats='past-14-days'), lambda: get_post_past_day_stats(-14)),
            'past-30-days': ('过去30天文章发表数量', url_for('admin.index', stats='past-30-days'), lambda: get_post_past_day_stats(-30)),
            'this-year': ('今年文章发表数量', url_for('admin.index', stats='this-year'), lambda: get_post_year_status()),
        }

        stats = request.args.get('stats', default='this-week')
        stats_data = stats_actions[stats][2]()
        post_stats = stats2data(stats_data)

        return self.render('admin/dashboard.html',
                           user_total=user_total,
                           post_total=post_total,
                           comment_total=comment_total,
                           tag_total=tag_total,
                           post_stats=post_stats,
                           stats_actions=stats_actions)

    @expose('/login', methods=('GET', 'POST'))
    def login_view(self):
        """handle user login"""
        from .forms import LoginForm

        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            redirect_url = request.args.get('next') or url_for('admin.index')
            return redirect(redirect_url)

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

            redirect_url = request.args.get('next') or url_for('admin.index')
            return redirect(redirect_url)

        href = url_for('.login_view')
        link = f'<p>已有帐号？请点击<a href="{href}">登录</a>。</p>'
        return render_template('auth/register.html', form=form, link=link)

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))
