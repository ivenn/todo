import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from config import config, log_dir


bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'main.login'
lm.login_message_category = "info"


def create_app(config_name):
    # initialize application
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # initialize extentions
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    lm.init_app(app)

    # initialize base loggers configuration
    from logging_config import LOGGERS
    import logging.config
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    logging.config.dictConfig(LOGGERS[app.config['LOGGER_CONFIG']])

    # register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from app.api_1 import api_1 as api_1_blueprint
    app.register_blueprint(api_1_blueprint, url_prefix='/api/1.0')

    return app
