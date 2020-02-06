from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin


db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')


def register_extensions(app):
    db.init_app(app)
    admin.init_app(app)
    from app.admin_ import register_modelviews
    register_modelviews(admin, app)
