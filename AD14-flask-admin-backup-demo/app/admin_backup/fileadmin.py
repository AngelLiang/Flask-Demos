from flask import current_app, url_for, redirect, flash
from flask_admin import expose
from flask_admin.contrib.fileadmin import FileAdmin


class BackupFileAdmin(FileAdmin):
    can_mkdir = False
    can_upload = False
    can_download = False
    can_delete_dirs = False

    can_rename = False  # 不能修改名字，否则无法恢复备份
    default_sort_column = 'date'
    default_desc = True

    can_restore = True
    list_template = 'admin/file/custom_list.html'

    @expose('/restore/<path:path>', methods=['GET', 'POST'])
    def restore(self, path):
        flask_admin_backup = current_app.extensions['flask-admin-backup']
        succ, fails = flask_admin_backup.restore(path)
        flash(f'恢复成功{len(succ)}条数据，恢复失败{len(fails)}条数据')
        return redirect(url_for('.index_view'))
