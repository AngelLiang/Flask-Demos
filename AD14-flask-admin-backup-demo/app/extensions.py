
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from app.admin_backup import FlaskAdminBackup

db = SQLAlchemy()
admin = Admin(template_mode='bootstrap3')
admin_backup = FlaskAdminBackup()
