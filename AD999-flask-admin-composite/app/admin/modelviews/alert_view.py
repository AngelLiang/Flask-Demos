from app.extensions import db, admin
from app.models import Alert
from .base import ModelView


class AlertModelView(ModelView):
    # column
    column_list = ('title', 'created_at',)
    column_default_sort = ('created_at', True)

    can_view_details = True


admin.add_view(AlertModelView(Alert, db.session, name='通知'))
