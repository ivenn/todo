import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask.ext.login import UserMixin
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from . import db, lm


user_tasklist = db.Table('user_tasklist',
                         db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                         db.Column('tasklist_id', db.Integer, db.ForeignKey('tasklist.id')),
                         db.PrimaryKeyConstraint('user_id', 'tasklist_id'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(100), unique=True)
    confirmed = db.Column(db.Boolean, default=False)

    tasks = db.relationship('Task', backref='user')
    tasklists = db.relationship('TaskList', secondary=user_tasklist, backref='user')

    @property
    def password(self, password):
        raise AttributeError('password is not readable User property!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def confirm(self):
        self.confirmed = True
        db.session.add(self)
        db.session.commit()

    def is_confirmed(self):
        return self.confirmed

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def is_username_valid(username):
        return re.sub('[^a-zA-Z0-9]', '', username) == username

    @staticmethod
    def is_user_exists(username):
        return bool(User.query.filter_by(username=username).first())

    @staticmethod
    def is_email_exists(email):
        return bool(User.query.filter_by(email=email).first())

    @staticmethod
    def add_user(new_user):
        db.session.add(new_user)
        db.session.commit()

    def get_task_lists(self):
        return TaskList.query.filter(TaskList.users.any(id=self.id)).all()

    def create_list(self, new_task_list):
        if new_task_list.name in [tl.name for tl in self.tasklists]:
            return "Task list %s already exists" % new_task_list.name
        self.tasklists.append(new_task_list)
        db.session.add(self)
        db.session.commit()

    def subscribe_user_to_list(self, user, task_list):
        if task_list in user.tasklists:
            return "User %s is already subscribed to %s list" % (user.username, task_list.name)
        user.tasklists.append(task_list)
        db.session.add(user)
        db.session.commit()

    def unsubscribe_from_list(self, task_list):
        self.tasklists.remove(task_list)
        db.session.add(self)
        db.session.commit()

        if not task_list.users:
            db.session.delete(task_list)
            db.session.commit()

    def generate_auth_token(self, expiration=36000):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user


@lm.user_loader
def load_user(userid):
    return User.query.get(userid)


class TaskList(db.Model):
    __tablename__ = 'tasklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.String(1024))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    tasks = db.relationship('Task', backref='tasklist', cascade="all, delete-orphan")
    users = db.relationship('User', secondary=user_tasklist, backref='tasklist')

    name_author_constraint = db.UniqueConstraint('name', 'author_id', name='unique_tlname_tlauthor')
    __table_args__ = (name_author_constraint,)


    def add_task(self, new_task):
        if new_task.name in [t.name for t in self.tasks]:
            return "Task list %s already has task with name '%s'" % (self.name, new_task.name)
        self.tasks.append(new_task)
        db.session.add(self)
        db.session.commit()

    def delete_task(self, task):
        self.tasks.remove(task)
        db.session.commit()


class Task(db.Model):
    __tablename__ = 'task'

    TASK_STATE_OPEN = 'open'
    TASK_STATE_IN_PROGRESS = 'in_progress'
    TASK_STATE_DONE = 'done'
    TASK_STATES = [TASK_STATE_OPEN, TASK_STATE_IN_PROGRESS, TASK_STATE_DONE]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), index=True, nullable=False)
    description = db.Column(db.String(1024))
    state = db.Column(db.Enum(*TASK_STATES)) 
    due_datetime = db.Column(db.DateTime())

    tasklist_id = db.Column(db.Integer, db.ForeignKey('tasklist.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Task %r: %s>' % (self.name, self.description)

    def update_state(self, state):
        if state not in Task.TASK_STATES:
            raise Exception('Not valid state to update')
        self.state = state
        db.session.add(self)
        db.session.commit()


