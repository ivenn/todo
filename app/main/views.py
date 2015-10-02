from flask import session, redirect, url_for, escape, request, render_template, g, flash, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

from app.models import User, Task, TaskList
from app.main import main
from app.main.forms import RegistrationForm, LoginForm, TaskForm, TaskListForm
from app.token import generate_confiramation_token, confirm_token
from app.email_sender import send_email
from logging import getLogger

_LOGGER = getLogger(__name__)


@main.before_request
def before_request():
    g.user = current_user


@main.route('/')
@main.route('/index')
def index():
    return redirect(url_for('main.login'))


@main.route('/registration', methods=['GET', 'POST'])
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
            send_email(to=form.email.data, subject='registration on toDo', template=html_mail)
        except Exception as e:
            _LOGGER.error("E-mail was not sent")
            _LOGGER.error("Exception: %s" % str(str(e)))
        flash("Welcome! Please, follow link from confirmation email to finish registration.", 'info')

        return redirect(url_for('main.login'))
    return render_template('registration.html', form=form)


@main.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    tlform = TaskListForm()

    if tlform.validate_on_submit():
        TaskList.add_task_list(g.user, TaskList(name=tlform.name.data, 
                                                description=tlform.description.data, 
                                                author_id=g.user.id))
        flash('Task %s was added successfully' % tlform.name.data, 'success')
        return redirect(url_for('main.personal'))
    return render_template('personal.html', 
                           user=g.user,
                           task_list=None,
                           tasks=[],
                           task_lists=g.user.get_task_lists(),
                           tform=None, tlform=tlform)


@main.route('/personal/list/<list_id>', methods=['GET', 'POST'])
@login_required
def user_lists(list_id):
    tform = TaskForm()
    tlist = TaskList.query.filter_by(id=int(list_id)).first()

    # check if list exists and user has access to it
    if not tlist or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)

    if tform.validate_on_submit():
        Task.add_task(Task(name=tform.name.data,
                           state=Task.TASK_STATE_OPEN,
                           user_id=g.user.id), 
                      task_list=tlist)
        flash('Task %s was added successfully' % tform.name.data, 'success')
        return redirect(url_for('main.user_lists', id=list_id))

    return render_template('personal.html',
                           user=g.user,
                           task_list=tlist,
                           tasks=Task.query.filter_by(tasklist_id=list_id).all(),
                           task_lists=[],
                           tform=tform, tlform=None)

@main.route('/personal/list/<list_id>/task/delete/<task_id>', methods=['GET'])
@login_required
def delete_task(list_id, task_id):
    tlist = TaskList.query.filter_by(id=int(list_id)).first()
    t = Task.query.filter_by(id=task_id).first()
    # check if list exists and user has access to it
    if not tlist or not t or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)

    tlist.delete_task(t)
    flash('Task %s was deleted' % t.name, 'success')
    return redirect(url_for('main.user_lists', list_id=list_id))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('main.personal'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user.verify_password(form.password.data):
            login_user(user)
            if not user.confirmed:
                flash('You registration is not finished, please, confirm your accout by link from email', 'info')
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
    except Exception as e:
        _LOGGER.error("Token wasn't confirmed: %s" % str(e))
        flash('The confirmation link is invalid or expired', 'danger')
        return redirect(url_for('main.login'))
    user = User.query.filter_by(username=username).first_or_404()
    if user.is_confirmed():
        flash('User was already confirmed, just login!', 'warning')
    else:
        user.confirm()
        flash("Your registration confirmed! Welcome!", 'success')
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
