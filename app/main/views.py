from flask import session, redirect, url_for, escape, request, render_template, g, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from ..models import User, Task
from . import main
from .forms import RegistrationForm, LoginForm, TaskForm
from app.token import generate_confiramation_token, confirm_token
from app.email_sender import send_email


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
                            email=form.email.data,
                            confirmed=False))

        token = generate_confiramation_token(form.name.data)
        print token
        confirm_url = url_for("main.confirmation", token=token, _external=True)
        html_mail = render_template('user/activate.html', confirm_url=confirm_url)
        try:
            send_email(to=form.email.data, subject='registration on toDO', template=html_mail)
        except Exception, e:
            print type(e), e
            print "E-mail was not sent"
        flash("Welcome! Please, follow link from confirmation email to finish registration.")

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

@main.route('/confirm/<token>')
def confirmation(token):
    try:
        username = confirm_token(token)
    except:
        flash('The confirmation link us invalid or expired')
    user = User.query.filter_by(username=username).first_or_404()
    if user.confirmed:
        flash('User was already confirmed, just login!')
    else:
        user.confirm()
        # db.session.add(user)
        # db.session.commit()
        flash("Your registration confirmed! Welcome!")
    return redirect(url_for('main.personal'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html', user=g.user)


