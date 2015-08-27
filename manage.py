from app.__init__ import create_app, db
from flask.ext.script import Manager

app = create_app()
manager = Manager(app)

if __name__ == "__main__":
    with app.app_context():
        from app.models import *
        db.create_all()
    manager.run()