from flask import flash, current_app, abort
from flask_admin.babel import ngettext, gettext
from flask_admin.actions import action


class AdminBackupModelViewMixin(object):

    can_backup = True

    def backup_models(self, models):
        flask_admin_bakcup = current_app.extensions['flask-admin-backup']
        classname = self.model.__name__
        return flask_admin_bakcup.create(classname, models)

    if can_backup:
        @action('backup', 'Backup', 'Are you sure you want to backup selected models?')
        def action_backup(self, ids):
            try:
                query = self.model.query.filter(self.model.id.in_(ids))
                models = query.all()

                self.backup_models(models)

                count = len(models)

                flash(ngettext('Model was successfully backup.',
                               '%(count)s models were successfully backup.',
                               count,
                               count=count))
            except Exception as ex:
                if not self.handle_view_exception(ex):
                    raise

                flash(gettext('Failed to backup models. %(error)s',
                              error=str(ex)), 'error')
