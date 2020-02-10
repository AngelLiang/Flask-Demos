from flask import request, redirect, url_for
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_login import current_user

from app.admin.mixins import AlertsMixin


class ModelView(AlertsMixin, _ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.model, 'can_edit', self.can_edit)
        setattr(self.model, 'can_view_details', self.can_view_details)

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))
