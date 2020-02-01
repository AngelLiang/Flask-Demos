from flask_admin.contrib.sqla import ModelView
from app.extensions import db, admin
from app.models import User, Post, Comment


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


admin.add_view(CommentModelView(Comment, db.session, name='评论'))
