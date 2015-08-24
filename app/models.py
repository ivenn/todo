from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean)
    email = db.Column(db.String(40), unique=True)

    tasks = db.relationship('Task', backref='user')

    @property
    def password(self, password):
        raise AttributeError('password is not readable User property!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def is_username_valid(username):
        return re.sub('[^a-zA-Z0-9]', '', username) == username

    @staticmethod
    def is_user_exists(username):
        return bool(User.query.filter_by(username=username).first())


class Task(db.Model):
    STATE_OPEN = 'open'
    STATE_IN_PROGRESS = 'in_progress'
    STATE_DONE = 'done'

    STATES = [STATE_OPEN, STATE_IN_PROGRESS, STATE_DONE]

    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120))
    state = db.Column(db.String(16))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Task %r>' % self.text