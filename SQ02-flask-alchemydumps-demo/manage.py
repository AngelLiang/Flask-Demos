from app import app, db, User, Post
from flask_script import Manager
from flask_alchemydumps import AlchemyDumps, AlchemyDumpsCommand
from faker import Faker

fake = Faker('zh_CN')

alchemydumps = AlchemyDumps()
alchemydumps.init_app(app, db)
manager = Manager(app)
manager.add_command('alchemydumps', AlchemyDumpsCommand)


@manager.command
def initdb():
    """Initialize database."""
    db.create_all()


@manager.command
@manager.option('-u', '--user', help='User count')
@manager.option('-p', '--post', help='Post count')
def initdata(user_count=3, post_count=10):
    """Initialize data."""

    db.drop_all()
    db.create_all()

    users = []
    for i in range(user_count):
        user = User(name=fake.name())
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    posts = []
    for i in range(post_count):
        post = Post(title=fake.sentence())
        posts.append(post)
    db.session.add_all(posts)
    db.session.commit()


@manager.command
def add_user():
    user = User(name=fake.name())
    db.session.add(user)
    db.session.commit()


@manager.command
def list_user():
    users = db.session.query(User).all()
    print(users)


if __name__ == "__main__":
    manager.run()
