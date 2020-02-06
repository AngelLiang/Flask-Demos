# coding=utf-8

import os
import os.path as op
import datetime as dt
import time
from functools import partial
import hashlib
import uuid

from jinja2 import Markup
from werkzeug.utils import secure_filename
from flask import current_app, url_for

from flask_admin import expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib import sqla
from flask_admin.form import (
    thumbgen_filename, FormOpts, ImageUploadField, ImageUploadInput
)
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.fields import InlineModelFormField, InlineFormWidget


from flask_admin.contrib.sqla import ModelView


def get_image_path():
    return current_app.config['IMAGES_FOLDER_PATH']


class ImageFileAdmin(FileAdmin):
    can_delete = False
    can_rename = False
    can_upload = False
    can_mkdir = False

    allowed_extensions = ('swf', 'jpg', 'gif', 'png')


DEFAULT_ENDPOINT = 'imagefileadmin.download'


def _generae_image_name(image_data):
    md5 = hashlib.md5(image_data).hexdigest()
    datetime_str = str(time.strftime(
        '%Y%m%d%H%M%S', time.localtime(time.time())))
    return f'{datetime_str}-{md5}'


def generate_image_name(obj, file_data):
    """
    :param obj:
    :param file_data: werkzeug.datastructures.FileStorage
    """
    postfix = file_data.content_type.split('/')[1]

    # image_data = file_data.stream.read()
    # name = _generae_image_name(image_data)

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
        super().__init__(label='图片',
                         namegen=generate_image_name,
                         base_path=lambda: get_image_path(),
                         endpoint=endpoint,
                         max_size=(800, 800, False),
                         thumbnail_size=(100, 100, True),
                         *args, **kwargs)


class CustomImageShowField(ImageUploadField):
    widget = ImageShow()

    def __init__(self, *args, endpoint=DEFAULT_ENDPOINT, **kwargs):
        super().__init__(label='图片',
                         namegen=generate_image_name,
                         base_path=lambda: get_image_path(),
                         endpoint=endpoint,
                         max_size=(800, 800, False),
                         thumbnail_size=None,
                         *args, **kwargs)


def _list_thumbnail(view, context, model, name):
    if not model.path:
        return ''

    html = f"""
        <a href="{url_for(DEFAULT_ENDPOINT, path=model.path)}" target="_blank">
            <img  src="{url_for(DEFAULT_ENDPOINT, path=thumbgen_filename(model.path))}">
        </a>
    """
    return Markup(html)


class ImageView(ModelView):

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': CustomImageUploadField()
    }


class ImageModelView(ImageView):
    pass

####################################################################


class ImageInlineFormWidget(InlineFormWidget):
    pass


class ImageInlineModelFormField(InlineModelFormField):
    widget = ImageInlineFormWidget()


class ImageInlineModelFormList(sqla.form.InlineModelFormList):
    form_field_type = ImageInlineModelFormField

    def display_row_controls(self, field):
        """返回 False 为了去掉 InlineModelForm 右上角的“删除”选项"""
        return False


class ImageInlineModelConverter(sqla.form.InlineModelConverter):
    inline_field_list_type = ImageInlineModelFormList


class ImageInlineModelForm(InlineFormAdmin):
    form_extra_fields = {
        'path': CustomImageUploadField()
    }


class ImageInlineModelFormOnlyShow(ImageInlineModelForm):
    form_label = '图片'
    form_widget_args = {
        'name': {
            'disabled': True
        },
        'path': {
            'disabled': True
        },
    }
    form_extra_fields = {
        'path': CustomImageShowField()
    }
