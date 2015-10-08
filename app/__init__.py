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
lm.login_message_category = "info"

# initialize base loggers configuration
from logging_config import LOGGERS_FOR_USE
import logging.config
logging.config.dictConfig(LOGGERS_FOR_USE[app.config['LOGGER_CONFIGURATION']])

# register blueprints
from app.main import main as main_blueprint
app.register_blueprint(main_blueprint)
from app.rest import rest as rest_blueprint
app.register_blueprint(rest_blueprint)

from models import User, Task
