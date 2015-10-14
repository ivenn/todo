import os
basedir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(basedir, 'tmp', 'log')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = 'ryhn_56_nols'
    MAIL_SERVER = os.environ.setdefault('MAIL_SERVER', '') or 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.setdefault('APP_MAIL_USERNAME', '') or 'todo-main@yandex.ru'
    MAIL_PASSWORD = os.environ.setdefault('APP_MAIL_PASSWORD', '') or '321odot'
    MAIL_DEFAULT_SENDER = os.environ.setdefault('APP_MAIL_USERNAME', '') or MAIL_USERNAME
    LOGGER_CONFIG = 'LOGGER'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@localhost/db1'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

class TestConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db1')

config = {'development': DevelopmentConfig,
          'default': DevelopmentConfig,
          'test': TestConfig}
