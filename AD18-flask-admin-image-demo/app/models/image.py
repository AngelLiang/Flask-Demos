import os
import os.path as op

from sqlalchemy import and_, or_
from sqlalchemy.event import listens_for
from sqlalchemy.orm import remote, foreign, foreign, remote, backref
from flask import current_app
from flask_admin.form import thumbgen_filename

from app.extensions import db


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    url = db.Column(db.String(255))

    # 通用外键，用于存储关联的数据
    discriminator = db.Column(db.String(64))
    object_id = db.Column(db.Integer, index=True)


@listens_for(Image, 'after_delete')
def delete_image(mapper, connection, target):

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


class HasImagesMixin(object):
    pass


@listens_for(HasImagesMixin, 'mapper_configured', propagate=True)
def setup_listener(mapper, class_):
    name = class_.__name__
    discriminator = name.lower()

    # 添加关系
    class_.images = db.relationship(
        Image,
        primaryjoin=and_(
            class_.id == foreign(remote(Image.object_id)),
            Image.discriminator == discriminator
        ),
        backref=backref(
            'object_%s' % discriminator,
            # uselist=False,
            primaryjoin=remote(class_.id) == foreign(Image.object_id)
        ),
    )

    @listens_for(class_.images, 'append')
    def append_image(target, value, initiator):
        value.discriminator = discriminator

    # @event.listens_for(class_.images, 'set')
    # def set_address(target, value, initiator):
    #     value.tablename = tablename
