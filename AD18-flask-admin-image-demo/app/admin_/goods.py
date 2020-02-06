from flask_admin.contrib.sqla import ModelView

from app.models import Image
from .image_view.image import CustomImageUploadField
from .image_view.image_field import ImageField
from .image_view.image_inline_form import ImageInlineModelForm
from .image_view.images_formatter import images_formatter


class GoodsModelView(ModelView):

    can_view_details = True

    column_formatters = {
        'images': images_formatter,
    }

    column_details_list = ('name', 'images',)

    form_columns = ('name', 'images',)

    # inline_models = [ImageInlineModelForm(Image), ]

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        # 'images': CustomImageUploadField(),
        'images': ImageField(),  # 表单额外的字段
    }
