
from flask_admin.contrib.sqla import ModelView
from app.extensions import db, admin
from app.models import User, Post, Tag
from app.admin_backup import AdminBackupModelViewMixin


class UserModelView(AdminBackupModelViewMixin,
                    ModelView):
    column_list = ('id', 'name', 'username')
    column_default_sort = 'id'

    can_delete = False
    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


admin.add_view(UserModelView(User, db.session))
