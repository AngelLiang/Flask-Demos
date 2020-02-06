from flask_admin.contrib.sqla import ModelView

from app.models import Image
from .image_field import images_formatter
from .image import ImageInlineModelForm


class GoodsModelView(ModelView):

    can_view_details = True

    column_formatters = {
        'images': images_formatter
    }
    inline_models = [ImageInlineModelForm(Image), ]

    column_details_list = ('name', 'images',)
