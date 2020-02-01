from flask_admin.contrib.sqla import ModelView as _ModelView


class ModelView(_ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.model, 'can_edit', self.can_edit)
        setattr(self.model, 'can_view_details', self.can_view_details)
