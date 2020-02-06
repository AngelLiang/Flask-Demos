import os.path as op
from flask import request
from wtforms import StringField

from .image import get_image_endpoint


class ImageInput(object):
    """
    Image upload controller, supports
    1. Multiple file upload one time
    2. Preview existing image files on server.
    3. Preview to be uploaded image files on the fly before uploading.
    Template file components/image_field.html is needed for this controller
    to work correctly.
    """

    def __call__(self, field, **kwargs):
        # Use field.data to get current data.
        from flask import render_template
        associated_images = []
        if ((field.data is not None and hasattr(field.data, 'filename') and len(field.data.filename) > 0)
                or (field.data is not None and hasattr(field.data, '__len__') and len(field.data) > 0)):
            for p_i in field.data:
                associated_images.append(p_i)
        else:
            associated_images = []
        return render_template('components/images_input.html',
                               associated_images=associated_images,
                               image_endpoint=get_image_endpoint())


class ImageField(StringField):
    widget = ImageInput()

    def __call__(self, **kwargs):
        return super(ImageField, self).__call__(**kwargs)

    def set_object_type(self, object_type):
        self.object_type = object_type

    def _delete_image(self, id, commit=False):
        from app.extensions import db
        from app.models.image import Image
        image = Image.query.get(id)
        db.session.delete(image)
        if commit:
            db.session.commit()

    def _save_image(self, file_data, commit=False):
        from app.extensions import db
        from app.models.image import Image

        from .image import ImageForm

        image = Image()
        form = ImageForm(image_upload=file_data)
        form.validate()  # 使用 form 保存图片
        form.image_upload.populate_obj(image, 'path')
        image.name = image.path

        db.session.add(image)
        if commit:
            db.session.commit()
        return image

    def delete_images_handle(self):
        """处理要删除的图片"""
        images_to_del = request.form.get('images-to-delete')
        if len(images_to_del) > 0:
            to_del_ids = images_to_del.split(',')
            for to_del_id in to_del_ids:
                self._delete_image(to_del_id, commit=False)

    def save_images_handle(self, obj, name):
        """处理需要保存的图片"""
        files = request.files.getlist('images_placeholder')
        images = getattr(obj, name)
        for f in files:
            if len(f.filename) > 0:
                image = self._save_image(f)
                images.append(image)
        setattr(obj, name, images)

    def populate_obj(self, obj, name):
        self.delete_images_handle()
        self.save_images_handle(obj, name)
