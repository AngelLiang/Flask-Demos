from flask_admin.contrib.sqla import ModelView
from app.extensions import db, admin
from app.models import User, Post


class PostModelView(ModelView):
    column_list = ('title', 'created_at', 'user')
    column_default_sort = ('created_at', True)

    form_ajax_refs = {
        'user': {
            'fields': (User.name,)
        }
    }


admin.add_view(PostModelView(Post, db.session, name='文章'))
