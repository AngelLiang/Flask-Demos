from .base import ModelView


class UserModelView(ModelView):
    column_list = ('id', 'name', 'username', 'created_at')
    column_default_sort = 'id'

    can_delete = False

    # view_details
    column_details_exclude_list = ('password_hash',)
    can_view_details = True

    # export
    can_export = True
    export_max_rows = 1000
    export_types = ('csv', 'xls')

    # form
    form_excluded_columns = ('password_hash',)
