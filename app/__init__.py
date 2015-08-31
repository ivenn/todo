from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.login import LoginManager

from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'main.login'

def create_app(config_name='default'):
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    lm.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        from models import User, Task
        db.create_all()

    return app


