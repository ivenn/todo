from app import db, app
from flask.ext.script import Manager

manager = Manager(app)

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


if __name__ == "__main__":
    manager.run()