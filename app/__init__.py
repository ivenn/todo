import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask.ext.mail import Mail

from config import config

# initialize application
app = Flask(__name__)
app.config.from_object(config[os.environ.setdefault('APP_SETTINGS', 'default')])

# initialize extentions
bootstrap = Bootstrap()
bootstrap.init_app(app)
moment = Moment()
moment.init_app(app)
mail = Mail()
mail.init_app(app)
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'main.login'

# initialize logging
log_path = app.config['LOGS_FILE_PATH']
try:
    os.makedirs(log_path)
except OSError as exc:
    if exc.errno == os.errno.EEXIST and os.path.isdir(log_path):
        pass
    else: raise

import logging
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(log_path + 'todolist.log', mode='a', maxBytes=1024*1024*1024, backupCount=5)
if not app.debug:
    file_handler.setLevel(logging.INFO)
else:
    file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter('%(asctime)s [%(levelname)5s]: %(name)s %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)
if not app.debug:
    app.logger.setLevel(logging.INFO)
    app.logger.info('ToDOlist startup')
else:
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('ToDOlist startup')
    app.logger.debug('will be used debug log level')
from logging import getLogger
logger = getLogger('sqlalchemy')
logger.setLevel(logging.ERROR)
logger.addHandler(file_handler)


from app.main import main as main_blueprint
app.register_blueprint(main_blueprint)

from models import User, Task


