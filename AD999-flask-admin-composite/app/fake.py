import random
from faker import Faker

from app.extensions import db
from app.models import User, Post, Tag, Comment, Alert

fake = Faker('zh_CN')


def fake_admin(username='admin', password='admin'):
    admin = User(username=username)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()


def initdata(user_count=50, post_count=500, tag_count=20, comment_count=800, alert_count=10):

    users = []
    for i in range(user_count):
        user = User(
            name=fake.name(),
            username=fake.profile()['username'],
            created_at=fake.past_datetime(),
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    tags = []
    for i in range(tag_count):
        tag = Tag(name=fake.word())
        tags.append(tag)
    db.session.add_all(tags)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(
            title=fake.sentence(),
            tags=list(set([
                Tag.query.get(random.randrange(1, Tag.query.count())),
                Tag.query.get(random.randrange(1, Tag.query.count())),
                Tag.query.get(random.randrange(1, Tag.query.count()))
            ])),
            user_id=random.randrange(1, User.query.count()),
            created_at=fake.date_time_between(start_date='-35d')
        )
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()

    comments = []
    for i in range(comment_count):
        comment = Comment(
            content=fake.sentence(),
            user_id=random.randrange(1, User.query.count()),
            post_id=random.randrange(1, Post.query.count()),
            created_at=fake.date_time_between(start_date='-35d')
        )
        comments.append(comment)
    db.session.add_all(comments)
    db.session.commit()

    alerts = []
    for i in range(alert_count):
        alert = Alert(
            title=fake.sentence(),
            content=fake.sentence(),
            created_at=fake.past_datetime()
        )
        alerts.append(alert)
    db.session.add_all(alerts)
    db.session.commit()
