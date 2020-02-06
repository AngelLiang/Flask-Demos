from app.models import User, Post

from .base import ModelView
from app.admin.formatters import user_formatter, tags_formatter


class PostModelView(ModelView):
    # column
    column_list = ('title', 'tags', 'created_at', 'user')
    column_default_sort = ('created_at', True)
    column_searchable_list = ('title',)

    column_filters = ('tags.name',)

    # form
    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        }
    }

    column_formatters = {
        'user': user_formatter,
        'tags': tags_formatter
    }

    # for object_ref
    line_fields = [
        {
            'label': 'name',
            'field': 'name'
        },
        {
            'label': 'username',
            'field': 'username'
        }
    ]

