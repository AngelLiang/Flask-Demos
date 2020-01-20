import os
import gzip
from time import gmtime, strftime

from .common import get_timestamp


class LocalTools(object):
    """Manage backup directory and files in local file system"""

    def __init__(self, backup_path):
        self.path = self.normalize_path(backup_path)

    @property
    def TIMESTAMP(self):
        return strftime('%Y%m%d%H%M%S', gmtime())

    @staticmethod
    def normalize_path(path):
        """Creates the backup directory (if needed) and returns its absolute path

        :return: (str) Absolue path to the backup directory
        """
        if not os.path.exists(path):
            os.mkdir(path)
        return os.path.abspath(path) + os.sep

    def get_files(self):
        """List all files in the backup directory"""
        for name in os.listdir(self.path):
            is_file = os.path.isfile(os.path.join(self.path, name))
            has_timestamp = get_timestamp(name)
            if is_file and has_timestamp:
                yield name

    def create_file(self, name, contents):
        """Creates a gzip file

        :param name: (str) Name of the file to be created (without path)
        :param contents: (bytes) Contents to be written in the file

        :return: (str) path of the created file
        """
        file_path = os.path.join(self.path, name)
        with gzip.open(file_path, 'wb') as handler:
            handler.write(contents)
        return file_path

    def read_file(self, name):
        """Reads the contents of a gzip file

        :param name: (str) Name of the file to be read (without path)

        :return: (bytes) Content of the file
        """
        file_path = os.path.join(self.path, name)
        with gzip.open(file_path, 'rb') as handler:
            return handler.read()

    def delete_file(self, name):
        """
        Delete a file
        :param name: (str) Name of the file to be deleted (without path)
        """
        os.remove(os.path.join(self.path, name))
