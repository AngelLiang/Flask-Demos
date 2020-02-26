# coding=utf-8

import platform
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
from flask_admin.babel import gettext, lazy_gettext
from flask_admin.form import BaseForm
from wtforms import fields, validators
import tablib


temppath = tempfile.gettempdir()

IS_WINDOWS = platform.system() == 'Windows'


def str2bool(s):
    return s.lower() not in ('0', 'n', 'no', 'f', 'false')


class ModelViewImportMixin(object):
    """导入模型混入类"""

    can_import = True

    list_template = 'admin/model/list_with_import.html'
    import_template = 'admin/model/import_view.html'

    form_base_class = BaseForm
    import_types = ('xls', 'xlsx', 'csv', 'json')
    import_title = 'Import'
    import_template_filename = None
    import_columns = None
    import_exclude_columns = None
    column_import_list = []

    delete_after_import = True  # 导入成功后删除文件

    import_path = temppath
    storage = LocalFileStorage(import_path)

    def set_path(self, path):
        self.import_path = path
        self.storage = LocalFileStorage(path)

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

        # 检查文件是否存在
        # if self.storage.path_exists(filename):
        #     secure_name = self._separator.join([path, secure_filename(form.upload.data.filename)])
        #     raise Exception(gettext('File "%(name)s" already exists.', name=secure_name))
        # else:
        #     self.save_file(filename, form.upload.data)
        #     self.on_file_upload(directory, path, filename)

        # 如果文件存在则删除
        if self.storage.path_exists(filename):
            self.delete_file(filename)
        # 保存文件
        self.save_file(filename, form.upload.data)
        self.on_file_upload(directory, path, filename)
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

        if self.import_types and ext not in self.import_types:
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

    def get_import_columns(self):
        if self.import_columns:
            return self.import_columns
        return self.get_export_columns()

    def _import_data(self, filename):
        ext = op.splitext(filename)[1].lower()
        if ext.startswith('.'):
            ext = ext[1:]

        mode = 'r' if ext == 'csv' else 'rb'
        with open(filename, mode) as fh:
            data = tablib.Dataset().load(fh, format=ext)

        import_columns = self.get_import_columns()
        import_columns_mapping = dict(import_columns)
        column_name_mapping = {v: k for k, v in import_columns_mapping.items()}
        column_formatter = self.get_column_import_formatter()

        models = []
        for item in data.dict:
            obj = self.model()
            for k, v in item.items():
                column_name = column_name_mapping.get(k)
                if column_name:
                    formatter = column_formatter.get(column_name)
                    if formatter:
                        setattr(obj, column_name, formatter(v))
            models.append(obj)

        return models

    def get_template_name(self):
        return self.import_template_filename or f'{self.model.__name__}_template.xls'

    def get_upload_form(self):
        """
            Upload form class for file upload view.

            Override to implement customized behavior.
        """
        class UploadForm(self.form_base_class):
            """
                File upload form. Works with FileAdmin instance to check if it
                is allowed to upload file with given extension.
            """
            upload = fields.FileField(lazy_gettext('File to upload'))

            def __init__(self, *args, **kwargs):
                super(UploadForm, self).__init__(*args, **kwargs)
                self.admin = kwargs['admin']

            def validate_upload(self, field):
                if not self.upload.data:
                    raise validators.ValidationError(gettext('File required.'))

                filename = self.upload.data.filename

                if not self.admin.is_file_allowed(filename):
                    raise validators.ValidationError(
                        gettext('Invalid file type.'))

        return UploadForm

    def upload_form(self):
        """
            Instantiate file upload form and return it.

            Override to implement custom behavior.
        """
        upload_form_class = self.get_upload_form()
        if request.form:
            # Workaround for allowing both CSRF token + FileField to be submitted
            # https://bitbucket.org/danjac/flask-wtf/issue/12/fieldlist-filefield-does-not-follow
            formdata = request.form.copy()  # as request.form is immutable
            formdata.update(request.files)

            # admin=self allows the form to use self.is_file_allowed
            return upload_form_class(formdata, admin=self)
        elif request.files:
            return upload_form_class(request.files, admin=self)
        else:
            return upload_form_class(admin=self)

    @expose('/import/', methods=['GET', 'POST'])
    def import_view(self):
        return_url = url_for('.index_view')

        # path = self.import_filepath
        path = None
        base_path, directory, path = self._normalize_path(path)

        if not self.can_import:
            flash('导入数据被禁用', 'error')
            return redirect(return_url)

        form = self.upload_form()

        if request.method == 'POST' and form.validate():
            # current_app.logger.debug(f'upload:{form.upload.data.filename}')
            try:
                filename = self._save_form_files(directory, path, form)
            except Exception as ex:
                flash(gettext('Failed to save file: %(error)s', error=ex), 'error')
            else:
                # current_app.logger.debug(f'Save path: {filename}')
                try:
                    # 导入数据
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

        template = self.import_template
        return self.render(template, form=form, cancel_url=return_url)

    @expose('/import/template-file/', methods=['GET'])
    def get_import_template_file(self):
        """获取导入数据的模板文件"""
        format = request.args.get('format', 'xls')
        filename = self.get_template_name()

        disposition = f'attachment;filename={filename}'

        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = 'application/octet-stream'
        if encoding:
            mimetype = '%s; charset=%s' % (mimetype, encoding)

        columns = self.get_import_columns()
        headers = [c[1] for c in columns]
        ds = tablib.Dataset(headers=headers)
        response_data = ds.export(format=format)

        return Response(
            response_data,
            headers={'Content-Disposition': disposition},
            mimetype=mimetype,
        )
