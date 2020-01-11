
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'
# login_manager.login_message = '请先登录'

from .admin import AdminIndexView
admin = Admin(template_mode='bootstrap3', index_view=AdminIndexView())
