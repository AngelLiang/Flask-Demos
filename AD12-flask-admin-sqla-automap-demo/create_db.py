from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapper, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dburl = 'sqlite:///data.sqlite'

engine = create_engine(dburl, convert_unicode=True)
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
# metadata = MetaData()
metadata = Base.metadata

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50), unique=True),
    Column('email', String(120), unique=True)
)

posts = Table(
    'posts', metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(128)),
    Column('content', Text())
)

tags = Table(
    'tags', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(64))
)

posts_tags_table = Table(
    'posts_tags', metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    con = engine.connect()
    con.execute(users.insert(), name='admin', email='admin@localhost')
    for i in range(20):
        con.execute(users.insert(),
                    name=f'user{i}',
                    email=f'user{i}@localhost')


if __name__ == "__main__":
    init_db()
