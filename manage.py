import os
from app import create_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from app import db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def create_admin():
    from app.models import User
    User.add_user(User(username='admin',
                       password='admin',
                       is_admin=True,
                       email='admin@toDo.com',
                       confirmed=True))

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()