from flask.ext.sqlalchemy import SQLAlchemy
import re

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, index=True)
    password = db.Column(db.String(40))
    is_admin = db.Column(db.Boolean)
    email = db.Column(db.String(40), unique=True)

    tasks = db.relationship('Task', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def is_username_valid(username):
        return True

    @staticmethod
    def is_user_unique(username):
        if User.query.filter_by(username=username).first():
            return False
        else:
            return True

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