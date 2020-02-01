import os
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from .backup import Backup
from .serializer import Serializer
from .autoclean import BackupAutoClean

from .mixins import AdminBackupModelViewMixin
from .fileadmin import BackupFileAdmin


class FlaskAdminBackup:
    def __init__(self, app=None, db=None, admin=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app, db=None, admin=None, backup=None, serializer=None):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask-admin-backup'] = self

        app.config.setdefault('ADMIN_BACKUP_FOLDER_NAME', 'databackup')
        app.config.setdefault('ADMIN_BACKUP_PATH', os.getcwd())
        app.config.setdefault('ADMIN_BACKUP_PREFIX', 'db-bkp')
        app.config.setdefault('ADMIN_BACKUP_FILEADMIN_NAME', 'Backup')

        self.app = app
        self.db = db
        self.fileadmin_name = self.app.config['ADMIN_BACKUP_FILEADMIN_NAME']
        self.prefix = self.app.config['ADMIN_BACKUP_PREFIX']
        self.folder_path = os.path.join(
            self.app.config['ADMIN_BACKUP_PATH'],
            self.app.config['ADMIN_BACKUP_FOLDER_NAME'])

        self.backup = backup or Backup(
            path=self.folder_path, prefix=self.prefix)
        self.target = self.backup.get_target()
        self.serializer = serializer or Serializer(db=db)

        if admin:
            self.add_file_view(admin)

    def add_file_view(self, admin):
        admin.add_view(BackupFileAdmin(
            self.folder_path,
            name=self.fileadmin_name))

    def create(self, class_name, contents):
        """备份数据
        :param class_name: str,
        :param contents: list,

        :return: bool
        """
        data = self.serializer.dump_data(contents)
        filename = self.backup.generate_name(class_name)  # 生成文件名称
        full_path = self.target.create_file(filename, data)

        rows = len(self.serializer.load_data(data))
        if full_path:
            print('==> {} rows from {} saved as {}'.format(
                rows, class_name, full_path))
            return True
        else:
            print('==> Error creating {} at {}'.format(
                filename, self.target.path))
            return False

    def restore(self, path):
        """恢复数据

        :param path: 备份文件路径
        """
        contents = self.target.read_file(path)
        successes = []
        fails = []

        db = self.db

        rows = self.serializer.load_data(contents)
        for row in rows:
            try:
                db.session.merge(row)  # 使用了 db.session.merge
                db.session.commit()  # 是否可以换成 flush ？
                successes.append(row)
            except (IntegrityError, InvalidRequestError):
                db.session.rollback()
                fails.append(row)

        return successes, fails

    def autoclean(self):
        """
        Remove a series of backup files based on the following rules:

        * Keeps all the backups from the last 7 days
        * Keeps the most recent backup from each week of the last month
        * Keeps the most recent backup from each month of the last year
        * Keeps the most recent backup from each year of the remaining years
        """
        backup = self.backup
        backup.files = tuple(backup.target.get_files())
        if not backup.files:
            print('==> No backups found.')
            return None
        cleaning = BackupAutoClean(backup.get_timestamps())
        white_list = cleaning.white_list
        black_list = cleaning.black_list
        if not black_list:
            print('==> No backup to be deleted.')
            return None
