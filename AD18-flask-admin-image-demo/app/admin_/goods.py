from flask_admin.contrib.sqla import ModelView

from .image_view.image_field import ImageField
from .image_view.images_formatter import images_formatter


class GoodsModelView(ModelView):

    can_view_details = True

    column_formatters = {
        'images': images_formatter,
    }
    column_details_list = ('name', 'images',)

    form_columns = ('name', 'images',)
    form_extra_fields = {
        'images': ImageField(),
    }
