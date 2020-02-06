from flask_admin.contrib import sqla
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.fields import InlineModelFormField, InlineFormWidget

from .image import CustomImageUploadField, CustomImageShowField


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
    column_labels = {
        'name': '图片名称',
        'path': '路径',
    }
    form_columns = ('id', 'name', 'path')
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
