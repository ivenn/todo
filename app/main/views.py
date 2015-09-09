from flask import session, redirect, url_for, escape, request, render_template, g, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

from app.models import User, Task
from app.main import main
from app.main.forms import RegistrationForm, LoginForm, TaskForm
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
    if g.user.is_authenticated():
        return redirect(url_for('main.personal'))

    form = RegistrationForm()
    if form.validate_on_submit():
        User.add_user(User(username=form.name.data,
                            password=form.password.data,
                            email=form.email.data,
                            confirmed=False))

        token = generate_confiramation_token(form.name.data)
        confirm_url = url_for("main.confirmation", token=token, _external=True)
        html_mail = render_template('user/activate.html', confirm_url=confirm_url)
        try:
            send_email(to=form.email.data, subject='registration on toDO', template=html_mail)
        except Exception as e:
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
    if g.user.is_authenticated():
        return redirect(url_for('main.personal'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user.verify_password(form.password.data):
            login_user(user)
            if not user.confirmed: flash('You registration is not finished, please, confirm your accout by link from email')
            return redirect(url_for('main.personal'))
        else:
            form.password.errors.append('Invalid password')
    return render_template('login.html', form=form, user=g.user)

@main.route('/confirm/<token>')
def confirmation(token):
    if not g.user.is_anonymous() and g.user.is_confirmed():
        return redirect(url_for('main.personal'))
    try:
        username = confirm_token(token)
    except:
        flash('The confirmation link us invalid or expired')
    user = User.query.filter_by(username=username).first_or_404()
    if user.is_confirmed():
        flash('User was already confirmed, just login!')
    else:
        user.confirm()
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


