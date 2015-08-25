from flask import session, redirect, url_for, escape, request, render_template

from .. import db
from ..models import User, Task

from . import main
from .forms import RegistrationForm, LoginForm, TaskForm


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html', msg='', username=is_authenticated())


@main.route('/registration', methods=['GET','POST'])
def registration():
    if 'username' in session:
        redirect(url_for('main.personal'))
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


@main.route('/personal', methods=['GET', 'POST'])
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
        return redirect(url_for('main.login'))

@main.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        if 'username' in session:
            return redirect(url_for('main.personal'))
        else:
            return render_template('login.html', form=form, username=is_authenticated())
    elif request.method == 'POST':
        if 'username' in session:
            return redirect(url_for('main.personal'))
        else:
            if form.validate_on_submit():
                user = User.query.filter_by(username=form.name.data).first()
                if user.verify_password(form.password.data):
                    session['username'] = form.name.data
                    return redirect(url_for('main.personal'))
                form.password.errors.append('Invalid password')
            return render_template('login.html', form=form, username=is_authenticated())


@main.route('/logout', methods=['GET'])
def logout():
    if 'username' in session:
        session.pop('username')
        return redirect(url_for('main.login'))
    else:
        return render_template('index.html', msg='You is not logged in')


@main.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html', username=is_authenticated())


def is_authenticated():
    """
    @:return: User name if user is Authenticated in another case None

    """
    return session['username'] if 'username' in session else None

