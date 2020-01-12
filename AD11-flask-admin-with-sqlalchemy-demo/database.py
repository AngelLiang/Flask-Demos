from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

dburl = 'sqlite:///data.sqlite'

engine = create_engine(dburl, convert_unicode=True)
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
# metadata = MetaData()
metadata = Base.metadata


def init_db(app):
    # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
    # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()


def init_data(db_session, user_count=20):
    from .models import users
    con = engine.connect()
    con.execute(users.insert(), name='admin', email='admin@localhost')
