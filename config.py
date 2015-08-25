import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root123@localhost/db1'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

config = {'development': DevelopmentConfig,
		  'default': DevelopmentConfig}
