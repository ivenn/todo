from flask import session, redirect, url_for, escape, request, render_template, g, flash, abort
from flask.ext.login import login_user, logout_user, login_required, current_user

from app.models import User, Task, TaskList
from app.main import main
from app.main.forms import RegistrationForm, LoginForm, TaskForm, TaskListForm, SubscribeForm
from app.token import generate_confiramation_token, confirm_token
from app.email_sender import send_email

from logging import getLogger

_log = getLogger(__name__)

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
            _log.error("E-mail was not sent")
            _log.error("Exception: %s" % str(str(e)))
        flash("Welcome! Please, follow link from confirmation email to finish registration.", 'info')

        return redirect(url_for('main.login'))
    return render_template('registration.html', form=form)


@main.route('/personal', methods=['GET', 'POST'])
@login_required
def personal():
    tlform = TaskListForm()

    if tlform.validate_on_submit():
        err = g.user.create_list(TaskList(name=tlform.name.data,
                                          description=tlform.description.data,
                                          author_id=g.user.id))
        if not err:
            flash('Task List %s was added successfully' % tlform.name.data, 'success')
        else:
            flash(err, 'warning')
        return redirect(url_for('main.personal'))
    return render_template('personal.html',
                           user=g.user,
                           task_list=None,
                           task_lists=g.user.get_task_lists(),
                           tform=None,
                           tlform=tlform,
                           sform=None)


@main.route('/personal/list/<list_id>', methods=['GET', 'POST'])
@login_required
def user_lists(list_id):
    tform = TaskForm()
    tlist = TaskList.query.filter_by(id=int(list_id)).first()

    # check if list exists and user has access to it
    if not tlist or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)

    if tform.validate_on_submit():
        err = tlist.add_task(Task(name=tform.name.data,
                                  state=Task.TASK_STATE_OPEN,
                                  user_id=g.user.id))
        if not err:
            flash('Task %s was added successfully' % tform.name.data, 'success')
        else:
            flash(err, 'warning')
        return redirect(url_for('main.user_lists', list_id=list_id))

    return render_template('personal.html',
                           user=g.user,
                           task_list=tlist,
                           task_lists=None,
                           tform=tform,
                           tlform=None,
                           sform=None)


@main.route('/personal/list/unsubscribe/<list_id>', methods=['GET'])
@login_required
def unsubscribe_from_list(list_id):
    tlist = TaskList.query.filter_by(id=int(list_id)).first()
    # check if list exists and user has access to it
    if not tlist or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)
    g.user.unsubscribe_from_list(tlist)
    flash("You was unsubscribed from Task List '%s'" % tlist.name, 'success')
    return redirect(url_for('main.personal'))


@main.route('/personal/list/subscribe/<list_id>', methods=['GET', 'POST'])
@login_required
def subscribe_user_to_list(list_id):
    tlist = TaskList.query.filter_by(id=int(list_id)).first()
    # check if list exists and user has access to it
    if not tlist or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)

    sform = SubscribeForm()
    if sform.validate_on_submit():
        u = User.query.filter_by(username=sform.subscriber.data,).first()
        err = g.user.subscribe_user_to_list(u, tlist)
        if not err:
            flash("You subscribed %s to Task List '%s'" % (u.username, tlist.name), 'success')
        else:
            flash(err, 'warning')
            return redirect(url_for('main.subscribe_user_to_list', list_id=list_id))
        return redirect(url_for('main.personal'))

    return render_template('personal.html',
                           user=g.user,
                           task_list=None,
                           task_lists=None,
                           tform=None,
                           tlform=None,
                           sform=sform)


@main.route('/personal/list/<list_id>/task/<task_id>/delete', methods=['GET'])
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


@main.route('/personal/list/<list_id>/task/<task_id>/update/<state>', methods=['GET'])
@login_required
def task_state(list_id, task_id, state):
    tlist = TaskList.query.filter_by(id=int(list_id)).first()
    t = Task.query.filter_by(id=task_id).first()
    # check if list exists and user has access to it
    if not tlist or not t or tlist.id not in [int(tl.id) for tl in g.user.get_task_lists()]:
        abort(404)

    t.update_state(state)
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
        _log.error("Token wasn't confirmed: %s" % str(e))
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
