# coding=utf-8

import os
import sys

BASEDIR = os.path.abspath(
    os.path.dirname(os.path.dirname(__file__))
)

from dotenv import load_dotenv  # noqa
dotenv_path = os.path.join(BASEDIR, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=True)

# SQLite URI compatible
WIN = sys.platform.startswith("win")
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


def os_getenv2bool(key, default='true'):
    return os.getenv(key, str(default)).lower() in ('1', 'yes', 'true')


class BaseConfig(object):
    APP_NAME = os.getenv('APP_NAME', 'flask-admin综合示例')

    # 修改默认的配置，以免和别的 flask app 发生登录帐号冲突
    SESSION_COOKIE_NAME = os.getenv(
        'SESSION_COOKIE_NAME', 'flask-admin-composite')
    # 配置 jsonify 是否排序
    JSON_SORT_KEYS = True

    SECRET_KEY = os.getenv('SECRET_KEY') or \
        'hard to guess string and longer than 32 byte!'

    # flask-sqlalchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    # SQLALCHEMY_ENGINE_OPTIONS = {
    #     # the number of connections to keep open inside the connection pool.
    #     'pool_size': 8,
    #     # this setting causes the pool to recycle connections after the given number of seconds has passed.
    #     # It defaults to -1, or no timeout.
    #     'pool_recycle': 7200,
    #     # number of seconds to wait before giving up on getting a connection from the pool.
    #     'pool_timeout': 30,
    #     'max_overflow': 10,
    # }

    @classmethod
    def init_app(cls, app):
        pass


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database
    SQLALCHEMY_ENGINE_OPTIONS = {}


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        prefix + os.path.join(BASEDIR, 'data-dev.db')
    )

    # jinja2模板自动加载
    TEMPLATES_AUTO_RELOAD = True
    # jinja2模板渲染跟踪
    EXPLAIN_TEMPLATE_LOADING = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        prefix + os.path.join(BASEDIR, 'data.db')
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
