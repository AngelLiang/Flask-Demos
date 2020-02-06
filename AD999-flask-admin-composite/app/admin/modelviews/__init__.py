from app.extensions import db
from app.models import User, Post, Comment, Tag, Alert

from .user_view import UserModelView
from .post_view import PostModelView
from .comment_view import CommentModelView
from .tag_view import TagModelView
from .alert_view import AlertModelView


def register_model_views(admin, app=None):
    admin.add_view(UserModelView(
        User, db.session, name='用户',
        menu_icon_type='glyph', menu_icon_value='glyphicon-user'))

    admin.add_view(PostModelView(Post, db.session, name='文章'))
    admin.add_view(CommentModelView(Comment, db.session, name='评论'))
    admin.add_view(TagModelView(Tag, db.session, name='标签'))
    admin.add_view(AlertModelView(Alert, db.session, name='通知'))
