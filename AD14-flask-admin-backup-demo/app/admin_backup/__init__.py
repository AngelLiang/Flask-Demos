import os
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from .local_tools import LocalTools
from .serializer import dump_data, load_data
from .mixins import AdminBackupModelViewMixin
from .fileadmin import BackupFileAdmin


class FlaskAdminBackup:
    def __init__(self, app=None, db=None, admin=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app, db=None, admin=None):
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
        self.target = self.get_target()
        self.models = []

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
        data = self.dump_data(contents)
        filename = self.generate_name(class_name)  # 生成文件名称
        full_path = self.target.create_file(filename, data)
        rows = len(self.load_data(data))
        if full_path:
            print('==> {} rows from {} saved as {}'.format(
                rows, class_name, full_path))
            return True
        else:
            print('==> Error creating {} at {}'.format(
                filename, self.target.path))
            return False

    def restore(self, path):
        contents = self.target.read_file(path)
        successes = []
        fails = []

        db = self.db

        for row in self.load_data(contents):
            try:
                db.session.merge(row)  # 使用了 db.session.merge
                db.session.commit()  # 是否可以换成 flush ？
                successes.append(row)
            except (IntegrityError, InvalidRequestError):
                db.session.rollback()
                fails.append(row)

        return successes, fails

    def get_target(self):
        return LocalTools(self.folder_path)

    def generate_name(self, class_name, timestamp=None):
        """
        Generate a backup file name given the timestamp and the name of the
        SQLAlchemy mapped class.
        """
        timestamp = timestamp or self.target.TIMESTAMP
        return '{}-{}-{}.gz'.format(self.prefix, timestamp, class_name)

    def get_timestamps(self):
        """
        Gets the different existing timestamp numeric IDs
        :param files: (list) List of backup file names
        :return: (list) Existing timestamps in backup directory
        """
        if not self.files:
            self.files = tuple(self.target.get_files())

        different_timestamps = list()
        for name in self.files:
            timestamp = self.target.get_timestamp(name)
            if timestamp and timestamp not in different_timestamps:
                different_timestamps.append(timestamp)
        return different_timestamps

    def by_timestamp(self, timestamp):
        """Gets the list of all backup files with a given timestamp

        :param timestamp: (str) Timestamp to be used as filter
        :param files: (list) List of backup file names

        :return: (list) The list of backup file names matching the timestamp
        """
        if not self.files:
            self.files = tuple(self.target.get_files())

        for name in self.files:
            if timestamp == self.target.get_timestamp(name):
                yield name

    def valid(self, timestamp):
        """Check backup files for the given timestamp"""
        if timestamp and timestamp in self.get_timestamps():
            return True
        print('==> Invalid id. Use "history" to list existing downloads')
        return False

    def dump_data(self, contents):
        return dump_data(self.db, contents)

    def load_data(self, contents):
        return load_data(self.db, contents)

    def get_mapped_classes(self):
        """Gets a list of SQLALchemy mapped classes"""
        db = self.db
        self.add_subclasses(db.Model)
        return self.models

    def add_subclasses(self, model):
        """Feed self.models filtering `do_not_backup` and abstract models"""
        if model.__subclasses__():
            for submodel in model.__subclasses__():
                self.add_subclasses(submodel)
        else:
            self.models.append(model)
