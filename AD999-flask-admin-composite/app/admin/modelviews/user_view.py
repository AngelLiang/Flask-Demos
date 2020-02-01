from flask_admin.contrib.sqla import ModelView
from app.extensions import db, admin
from app.models import User


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username', 'created_at')
    column_default_sort = 'id'

    can_export = True
    export_max_rows = 1000
    export_types = ['csv', 'xls']


admin.add_view(UserModelView(User, db.session, name='用户'))
