from datetime import datetime
import os

from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.script import Manager

from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length

class RegistrationForm(Form):
    name = StringField('Enter your name', validators=[Required(), Length(3, 32)])
    password = StringField('Enter your password', validators=[Required(), Length(3, 32)])
    email = StringField('Enter your email', validators=[Required(), Length(3, 32)])
    submit = SubmitField('Submit')

class LoginForm(Form):
    name = StringField('Username', validators=[Required(),])
    password = StringField('Password', validators=[Required(),])
    submit = SubmitField('Submit')

class TaskForm(Form):
    text = StringField('Task description', validators=[Required(),])
    submit = SubmitField('Add')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root123@localhost/db1'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['DEBUG'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

db = SQLAlchemy()
db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', msg='')


@app.route('/registration', methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if request.method == 'GET':
        return render_template('registration.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(username=form.name.data, password=form.password.data,
                            is_admin=False, email=form.email.data)
            db.session.add(new_user)
            db.session.commit()
            return render_template('index.html', msg='You was registered with %s username' % form.name.data)


@app.route('/personal', methods=['GET', 'POST'])
def personal():
    if 'username' in session:
        form = TaskForm()
        user_id = User.query.filter_by(username=session['username']).first().id

        if request.method == 'POST':
            if form.validate_on_submit():
                new_task = Task(text=form.text.data,
                                state=Task.STATE_OPEN, user_id=user_id)
                db.session.add(new_task)
                db.session.commit()
        return render_template('personal.html', username=session['username'], 
                                tasks=Task.query.filter_by(user_id=user_id), form=form)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('personal'))
        else:
            return render_template('login.html', form=form)
    elif request.method == 'POST':
        if 'username' in session:
            return redirect(url_for('personal'))
        else:
            if form.validate_on_submit():
                user = User.query.filter_by(username=form.name.data).first()
                if not user:
                    return render_template('index.html', msg='No such user %s' %form.name.data)
                else:
                    if user.password == form.password.data:
                        session['username'] = form.name.data
                        return redirect(url_for('personal'))
                    else:
                        return render_template('index.html', msg='Invalid password')


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('login'))
    else:
        return render_template('index.html', msg='You is not logged in')

@app.route('/time', methods=['GET'])
def time():
    return render_template('time.html', current_time=datetime.utcnow())

"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

app.secret_key = 'AMDN5V0Cdlgfd9jsdf55508djl'
"""


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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    manager.run()

