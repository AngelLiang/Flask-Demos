import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.automap import automap_base


dburl = os.getenv('DB_URL', 'sqlite:///data.sqlite')
engine = create_engine(dburl, convert_unicode=True)

Base = automap_base()
Base.prepare(engine, reflect=True)
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base.query = db_session.query_property()
metadata = Base.metadata


def init_db(app):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
