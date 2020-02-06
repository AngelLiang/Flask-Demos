import os
import os.path as op

from sqlalchemy.event import listens_for
from flask import current_app
from flask_admin.form import thumbgen_filename

from . import db


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    url = db.Column(db.String(255))


@listens_for(Image, 'after_delete')
def delelte_image(mapper, connection, target):

    file_path = current_app.config['IMAGES_FOLDER_PATH']

    if target.path:
        # Delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path, thumbgen_filename(target.path)))
        except OSError:
            pass
