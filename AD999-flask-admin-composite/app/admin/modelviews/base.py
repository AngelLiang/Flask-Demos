from flask_admin.contrib.sqla import ModelView as _ModelView
from app.admin.mixins import AlertsMixin


class ModelView(AlertsMixin, _ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.model, 'can_edit', self.can_edit)
        setattr(self.model, 'can_view_details', self.can_view_details)
