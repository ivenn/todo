from datetime import datetime
import os

from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.script import Manager

from forms import RegistrationForm, LoginForm, TaskForm
from models import User, Task, db


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 't0p s3cr3t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root123@localhost/db1'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['DEBUG'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

db.init_app(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', msg='')


@app.route('/registration', methods=['GET','POST'])
def registration():
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
        return render_template('registration.html', form=form)


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
                if user.verify_password(form.password.data):
                    session['username'] = form.name.data
                    return redirect(url_for('personal'))
                form.password.errors.append('Invalid password')
            return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('login'))
    else:
        return render_template('index.html', msg='You is not logged in')

"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

app.secret_key = 'AMDN5V0Cdlgfd9jsdf55508djl'
"""

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    manager.run()

