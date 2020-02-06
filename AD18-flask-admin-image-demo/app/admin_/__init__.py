from app import db
from app.models import Image, Goods
from .image_view.image_view import ImageFileAdmin, ImageModelView
from .goods import GoodsModelView


def register_modelviews(admin, app=None):
    admin.add_view(GoodsModelView(Goods, db.session))

    path = app.config['IMAGES_FOLDER_PATH']
    admin.add_view(ImageModelView(Image, db.session, path=path))
    # admin.add_view(ImageFileAdmin(path))
