import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = 'ryhn_56_nols'
    EMAIL_SERVER = 'mailtrap.io'
    MAIL_PORT = '2525'
    MAIL_USERNAME = '4352878fed3dd26e1'
    MAIL_PASSWORD = '8e3469cbab78f9'

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
