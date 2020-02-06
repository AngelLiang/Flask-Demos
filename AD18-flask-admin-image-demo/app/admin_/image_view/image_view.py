
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView

from .image import _list_thumbnail, CustomImageUploadField


class ImageFileAdmin(FileAdmin):
    can_delete = False
    can_rename = False
    can_upload = False
    can_mkdir = False

    allowed_extensions = ('swf', 'jpg', 'gif', 'png')


class ImageView(ModelView):

    column_formatters = {
        'path': _list_thumbnail
    }

    form_columns = ('name', 'path')

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': CustomImageUploadField()
    }


class ImageModelView(ImageView):
    column_list = ('name', 'path')
