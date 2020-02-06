from app.models import Post, Tag

from .base import ModelView


class TagModelView(ModelView):
    column_list = ('name',)
    column_default_sort = 'name'



