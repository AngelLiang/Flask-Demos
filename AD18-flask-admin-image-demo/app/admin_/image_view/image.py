import time
import uuid
import hashlib

from jinja2 import Markup
from werkzeug.utils import secure_filename
from flask import current_app, url_for
from flask_wtf import FlaskForm
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.form import thumbgen_filename, ImageUploadField, ImageUploadInput

DEFAULT_ENDPOINT = 'imagefileadmin.download'


def get_image_path():
    return current_app.config['IMAGES_FOLDER_PATH']


def generate_image_name(obj, file_data):
    """
    :param obj:
    :param file_data: werkzeug.datastructures.FileStorage
    """
    postfix = file_data.content_type.split('/')[1]
    name = uuid.uuid1()
    return f'{name}.{postfix}'


class CustomImageUploadInput(ImageUploadInput):

    def get_url(self, field):
        from flask_admin.helpers import get_url
        from flask_admin._compat import urljoin

        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = urljoin(field.url_relative_path, filename)

        return get_url(field.endpoint, path=filename)


class ImageUpload(CustomImageUploadInput):
    data_template = ('<div class="image">'
                     ' <img %(image)s>'
                     ' <input %(text)s>'
                     '</div>'
                     '<input %(file)s>')


class ImageShow(CustomImageUploadInput):
    data_template = ('<div class="image">'
                     ' <img %(image)s>'
                     '</div>')


class CustomImageUploadField(ImageUploadField):
    widget = CustomImageUploadInput()

    def __init__(self, *args, endpoint=DEFAULT_ENDPOINT, **kwargs):
        super().__init__(label='Image',
                         namegen=generate_image_name,
                         base_path=lambda: get_image_path(),
                         endpoint=endpoint,
                         max_size=(800, 800, False),
                         thumbnail_size=(100, 100, True),
                         *args, **kwargs)


class CustomImageShowField(ImageUploadField):
    widget = ImageShow()

    def __init__(self, *args, endpoint=DEFAULT_ENDPOINT, **kwargs):
        super().__init__(label='Image',
                         namegen=generate_image_name,
                         base_path=lambda: get_image_path(),
                         endpoint=endpoint,
                         max_size=(800, 800, False),
                         thumbnail_size=None,
                         *args, **kwargs)


class ImageForm(FlaskForm):
    image_upload = CustomImageUploadField()


def _list_thumbnail(view, context, model, name):
    if not model.path:
        return ''

    html = f"""
        <a href="{url_for(DEFAULT_ENDPOINT, path=model.path)}" target="_blank">
            <img  src="{url_for(DEFAULT_ENDPOINT, path=thumbgen_filename(model.path))}">
        </a>
    """
    return Markup(html)
