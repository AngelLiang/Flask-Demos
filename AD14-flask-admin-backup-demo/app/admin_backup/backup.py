
from .local_tools import LocalTools


DEFAULT_PATH = 'databackup'
DEFAULT_PRE = 'db-bkp'


class Backup(object):

    def __init__(self, path=DEFAULT_PATH, prefix=DEFAULT_PRE):
        self.path = path
        self.prefix = prefix
        self.files = None
        self.target = self.get_target()

    def get_target(self):
        return LocalTools(self.path)

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
        """
        Gets the list of all backup files with a given timestamp
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

    def generate_name(self, class_name, timestamp=None):
        """
        Gets a backup file name given the timestamp and the name of the
        SQLAlchemy mapped class.
        """
        timestamp = timestamp or self.target.TIMESTAMP
        return '{}-{}-{}.gz'.format(self.prefix, timestamp, class_name)
