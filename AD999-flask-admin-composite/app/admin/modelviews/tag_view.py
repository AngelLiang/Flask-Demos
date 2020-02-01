from flask_admin.contrib.sqla import ModelView
from app.extensions import db, admin
from app.models import Post, Tag


class TagModelView(ModelView):
    column_list = ('name',)
    column_default_sort = 'name'


admin.add_view(TagModelView(Tag, db.session, name='标签'))
