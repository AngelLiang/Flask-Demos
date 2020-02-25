# coding=utf-8

import os
import os.path as op
import mimetypes
import tempfile

from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from flask import Response
from flask import request
from flask import current_app
from flask import flash
from flask import redirect
from flask import url_for
from flask import abort
from flask_admin import expose
from flask_admin.babel import gettext
from flask_admin.contrib.fileadmin import LocalFileStorage
import tablib

from flask_admin.form import BaseForm
from .upload_form import UploadFormMixin

temppath = tempfile.gettempdir()


def str2bool(s):
    """
    如果 s 为 '1', 'yes', 'true' ，返回 True
    其他情况，比如为 '0', 'no', 'false' ，返回 False
    """
    return s.lower() in ('1', 'yes', 'true')


class ModelViewImportMixin(UploadFormMixin):
    """导入模型混入类"""

    can_import = True

    list_template = 'admin/model/list_with_import.html'
    import_template = 'admin/model/import_view.html'

    form_base_class = BaseForm
    import_types = ('xls', 'xlsx', 'csv')
    import_filepath = temppath
    import_title = 'Import'
    import_template_filename = None
    column_import_list = []
    allowed_extensions = import_types
    storage = LocalFileStorage(import_filepath)
    delete_after_import = False

    def _normalize_path(self, path):
        """
            Verify and normalize path.

            If the path is not relative to the base directory, will raise a 404 exception.

            If the path does not exist, this will also raise a 404 exception.
        """
        base_path = self.get_base_path()
        if path is None:
            directory = base_path
            path = ''
        else:
            path = op.normpath(path)
            if base_path:
                directory = self._separator.join([base_path, path])
            else:
                directory = path

            directory = op.normpath(directory)

            if not self.is_in_folder(base_path, directory):
                abort(404)

        if not self.storage.path_exists(directory):
            abort(404)

        return base_path, directory, path

    def _save_form_files(self, directory, path, form):
        """保存表单里的的文件"""
        filename = self._separator.join(
            [directory, secure_filename(form.upload.data.filename)]
        )

        # if self.storage.path_exists(filename):
        #     secure_name = self._separator.join([path, secure_filename(form.upload.data.filename)])
        #     raise Exception(gettext('File "%(name)s" already exists.', name=secure_name))
        # else:
        #     self.save_file(filename, form.upload.data)
        #     self.on_file_upload(directory, path, filename)

        if self.storage.path_exists(filename):
            # 如果存在则覆盖
            self.delete_file(filename)
        # 保存文件
        self.save_file(filename, form.upload.data)
        # self.on_file_upload(directory, path, filename)
        return filename

    @property
    def _separator(self):
        return self.storage.separator

    def on_file_upload(self, directory, path, filename):
        """
            Perform some actions after a file has been successfully uploaded.

            Called from upload method

            By default do nothing.
        """
        pass

    def is_file_allowed(self, filename):
        """
            Verify if file can be uploaded.

            Override to customize behavior.

            :param filename:
                Source file name
        """
        ext = op.splitext(filename)[1].lower()

        if ext.startswith('.'):
            ext = ext[1:]

        if self.allowed_extensions and ext not in self.allowed_extensions:
            return False

        return True

    def save_file(self, path, file_data):
        """
            Save uploaded file to the storage

            :param path:
                Path to save to
            :param file_data:
                Werkzeug `FileStorage` object
        """
        self.storage.save_file(path, file_data)

    def delete_file(self, file_path):
        self.storage.delete_file(file_path)

    def is_in_folder(self, base_path, directory):
        """
            Verify that `directory` is in `base_path` folder

            :param base_path:
                Base directory path
            :param directory:
                Directory path to check
        """
        return op.normpath(directory).startswith(base_path)

    def is_accessible_path(self, path):
        return True

    def get_base_path(self):
        return self.storage.get_base_path()

    def get_base_url(self):
        return self.base_url

    def export_columns_remove(self, export_columns):
        return export_columns

    def get_import_form(self):
        return self.get_create_form()

    # def import_form(self, obj=None):
    #     return self.create_form(obj=obj)

    def get_column_import_formatter(self):
        import datetime as dt
        from decimal import Decimal
        from sqlalchemy import inspect
        from sqlalchemy import String, Integer, Date, DateTime, Time, Float, Boolean, DECIMAL, Enum
        from dateutil.parser import parse

        model_columns = inspect(self.model).columns
        column_formatter = {}
        for c in model_columns:
            if isinstance(c.type, String):
                formatter = str
            elif isinstance(c.type, Integer):
                formatter = int
            elif isinstance(c.type, DateTime):
                formatter = parse
            elif isinstance(c.type, Boolean):
                formatter = str2bool
            elif isinstance(c.type, Float):
                formatter = float
            elif isinstance(c.type, Date):
                formatter = parse
            elif isinstance(c.type, Time):
                def formatter(s):
                    hour, minute, second = map(int, s.split(':'))
                    return dt.time(hour=hour, minute=minute, second=second)
            elif isinstance(c.type, DECIMAL):
                formatter = Decimal
            elif isinstance(c.type, Enum):
                formatter = None
            else:
                formatter = None
            column_formatter[c.name] = formatter
        return column_formatter

    def _import_data(self, filename):
        models = []

        with open(filename, 'r') as fh:
            data = tablib.Dataset().load(fh)

        column_formatter = self.get_column_import_formatter()
        # print(column_formatter)

        # form_cls = self.get_import_form()

        for item in data.dict:
            obj = self.model()
            for k, v in item.items():
                column_name = k.replace(' ', '_').lower()
                formatter = column_formatter.get(column_name)
                if formatter:
                    setattr(obj, column_name, formatter(v))
            models.append(obj)

        return models

    def generate_template_filename(self):
        return self.import_template_filename or f'{self.model.__name__}_template.xls'

    @expose('/import/', methods=['GET', 'POST'])
    def import_view(self):
        return_url = url_for('.index_view')

        # path = self.import_filepath
        path = None
        base_path, directory, path = self._normalize_path(path)

        if not self.can_import:
            flash('导入数据被禁用', 'error')
            return redirect(return_url)

        template = self.import_template
        form = self.upload_form()

        if request.method == 'POST' and form.validate():
            current_app.logger.debug(f'upload:{form.upload.data.filename}')
            try:
                filename = self._save_form_files(directory, path, form)
            except Exception as ex:
                flash(gettext('Failed to save file: %(error)s', error=ex), 'error')
            else:
                # 导入数据
                try:
                    models = self._import_data(filename)
                    self.session.add_all(models)
                    self.session.commit()
                except IntegrityError as e:
                    current_app.logger.info(e)
                    flash(f'导入失败，错误：{e}', 'error')
                else:
                    flash(f'成功导入 {len(models)} 条数据', 'success')
                    if self.delete_after_import:
                        self.delete_file(filename)  # 删除导入文件
                    return redirect(return_url)

        return self.render(template, form=form, cancel_url=return_url)

    @expose('/import/download-template/', methods=['GET'])
    def download_import_template(self):
        """下载导入数据的模板文件"""
        filename = self.generate_template_filename()

        disposition = f'attachment;filename={filename}'

        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = 'application/octet-stream'
        if encoding:
            mimetype = '%s; charset=%s' % (mimetype, encoding)

        columns = self.column_import_list
        headers = [self.get_columne_name(c) for c in columns]
        ds = tablib.Dataset(headers=headers)
        response_data = ds.export(format='xls')

        return Response(
            response_data,
            headers={'Content-Disposition': disposition},
            mimetype=mimetype,
        )
