import os
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from app import db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == "__main__":
    app.run()
