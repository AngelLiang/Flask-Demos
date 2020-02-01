from app.extensions import db, admin
from app.models import User, Post, Comment

from .base import ModelView
from app.admin.formatters import user_formatter


class CommentModelView(ModelView):
    column_list = ('content', 'created_at', 'post', 'user')
    column_default_sort = ('created_at', True)

    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        },
        'post': {
            'fields': (Post.title,)
        }
    }

    column_formatters = {
        'user': user_formatter,
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


admin.add_view(CommentModelView(Comment, db.session, name='评论'))
