from flask import session, redirect, url_for, escape, request, render_template, g
from flask.ext.login import login_user, logout_user, login_required, current_user

from ..models import User, Task
from . import main
from .forms import RegistrationForm, LoginForm, TaskForm


@main.before_request
def before_request():
    g.user = current_user


@main.route('/')
@main.route('/index')
def index():
    return redirect(url_for('main.login'))


@main.route('/registration', methods=['GET','POST'])
def registration():
    if g.user is not None and g.user.is_authenticated():
        redirect(url_for('main.personal'))

    form = RegistrationForm()
    if form.validate_on_submit():
        User.add_user(User(username=form.name.data,
                            password=form.password.data,
                            is_admin=False, email=form.email.data))
        return render_template('index.html', msg='You was registered with %s username' % form.name.data)
    return render_template('registration.html', form=form)


@main.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    form = TaskForm()

    if form.validate_on_submit():
        Task.add_task(Task(text=form.text.data, state=Task.STATE_OPEN, user_id=g.user.id))
    return render_template('personal.html', user=g.user, tasks=Task.query.filter_by(user_id=g.user.id),
                           form=form)


@main.route('/login', methods=['GET','POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('main.personal'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.personal'))
        else:
            form.password.errors.append('Invalid password')
    return render_template('login.html', form=form, user=g.user)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html', user=g.user)


