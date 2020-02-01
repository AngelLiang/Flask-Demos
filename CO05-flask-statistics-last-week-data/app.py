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


def get_post_week_stats(past=1):
    the_Monday = get_past_Monday(past)
    stats = db.session.query(
        Post.create_at, func.count(Post.id)
    ).filter(
        the_Monday <= Post.create_at,
        Post.create_at < the_Monday+datetime.timedelta(days=7)
    ).group_by(
        extract('day', Post.create_at)
    ).all()
    return stats


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
    # print(stats)

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
