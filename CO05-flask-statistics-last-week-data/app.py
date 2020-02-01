import datetime

from sqlalchemy import func, extract
from flask import Flask, request
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)
db.init_app(app)
db.app = app


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    text = db.Column(db.Text)
    create_at = db.Column(db.DateTime)

    def __str__(self):
        return f'{self.title}'


def get_past_Monday(past=1):
    """获取过去 past 的星期一的日期"""
    today = datetime.date.today()
    days = today.weekday() + past * 7
    return today - datetime.timedelta(days=days)


def get_stats_by_week(datetime_column, past=1, autofill=True):
    """
    :param datetime_column: ORM Column
    :param past: int, 过去的周数
    :param autofill: bool, 是否自动填充未来的数据
    """
    the_Monday = get_past_Monday(past)
    stats = db.session.query(
        datetime_column, func.count('*')
    ).filter(
        # 筛选大于等于某星期一，小于下星期一
        the_Monday <= datetime_column,
        datetime_column < the_Monday+datetime.timedelta(days=7)
    ).group_by(
        extract('day', datetime_column)
    ).all()

    # 如果达不到七天，应该填充剩下的数据
    if autofill:
        while len(stats) < 7:
            stats.append((stats[-1][0]+datetime.timedelta(days=1), 0))

    return stats


def get_post_week_stats(past=1, *args, **kwargs):
    return get_stats_by_week(Post.create_at, past, *args, **kwargs)


def stats2data(stats):
    data = [
        {'period': stat[0].strftime('%Y-%m-%d'), 'count': stat[1]}
        for stat in stats
    ]
    return data


@app.route('/')
def index():
    past = request.args.get('past', type=int, default=1)

    stats = get_post_week_stats(past)

    data = stats2data(stats)
    print(data)

    return render_template('index.html', data=data)


def initdata(post_count=100):
    from faker import Faker
    fake = Faker('zh_CN')

    db.drop_all()
    db.create_all()

    posts = []
    for i in range(post_count):
        post = Post(
            title=f'title{i+1}',
            create_at=fake.date_time_between(start_date='-14d', end_date='-2d')
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@app.before_first_request
def init_data():
    initdata()


if __name__ == "__main__":
    app.run(debug=True)
