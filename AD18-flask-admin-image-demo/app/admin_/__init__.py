import os

from app import db
from app.models import Image
from .image import ImageFileAdmin, ImageModelView


def register_modelviews(admin, app=None):

    admin.add_view(ImageModelView(Image, db.session))
    path = app.config['IMAGES_FOLDER_PATH']
    if not os.path.exists(path):
        os.mkdir(path)
    admin.add_view(ImageFileAdmin(path))
