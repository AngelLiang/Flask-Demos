# coding=utf-8

import os.path as op

from flask import request, flash, redirect
from flask_admin import expose
from flask_admin.babel import gettext, lazy_gettext
from flask_admin.form import BaseForm
from wtforms import fields, validators


class UploadFormMixin(object):

    upload_modal = True

    upload_template = 'admin/file/form.html'
    upload_modal_template = 'admin/file/modals/form.html'

    form_base_class = BaseForm
    allowed_extensions = None

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

    @expose('/upload/', methods=('GET', 'POST'))
    @expose('/upload/<path:path>', methods=('GET', 'POST'))
    def upload(self, path=None):
        """
            Upload view method

            :param path:
                Optional directory path. If not provided, will use the base directory
        """
        # Get path and verify if it is valid
        base_path, directory, path = self._normalize_path(path)

        if not self.can_upload:
            flash(gettext('File uploading is disabled.'), 'error')
            return redirect(self._get_dir_url('.index_view', path))

        if not self.is_accessible_path(path):
            flash(gettext('Permission denied.'), 'error')
            return redirect(self._get_dir_url('.index_view'))

        form = self.upload_form()
        if self.validate_form(form):
            try:
                self._save_form_files(directory, path, form)
                flash(gettext('Successfully saved file: %(name)s',
                              name=form.upload.data.filename), 'success')
                return redirect(self._get_dir_url('.index_view', path))
            except Exception as ex:
                flash(gettext('Failed to save file: %(error)s', error=ex), 'error')

        if self.upload_modal and request.args.get('modal'):
            template = self.upload_modal_template
        else:
            template = self.upload_template

        return self.render(template, form=form,
                           header_text=gettext('Upload File'),
                           modal=request.args.get('modal'))
