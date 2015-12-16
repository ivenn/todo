from flask import jsonify, make_response, session, request, g, abort, url_for
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask_httpauth import HTTPBasicAuth

from app.api_1 import api_1 as api
from app.models import User, Task, TaskList

from logging import getLogger

_log = getLogger(__name__)

auth = HTTPBasicAuth()


@api.before_request
def before_request():
    _log.debug("Request:\nHEAD:%sDATA: %s" % (request.headers, request.data))
    g.user = current_user


@api.after_request
def after_request(response):
    _log.debug("Response:%s" % (response))
    return response

# Error handlers

@api.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@api.errorhandler(409)
def conflict(error, description=None):
    return make_response(jsonify({'error': 'Conflict',
                                  'description': description}),
                         409)


@auth.verify_password
def verify_password(token, username=None):
    """
    Username are not used in this case,
    because we are use token based authentication
    """
    user = User.verify_auth_token(token)
    session_token = session['auth_token'] if 'auth_token' in session else None
    if session_token and session_token == token and user:
        return True
    return False


@api.route('/login', methods=['POST'])
def login():
    _log.info("login: %s" % request.json)
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return make_response(jsonify({'error': 'wrong request'}), 404)

    user = User.query.filter_by(username=request.json['username']).first()

    if user.verify_password(request.json['password']):
        login_user(user)
        if not user.confirmed:
            return make_response(jsonify({'error': 'You registration is not finished, \
                                                    please, confirm your accout by link from email'}),
                                 404)
        session['auth_token'] = g.user.generate_auth_token().decode('ascii')
        return make_response(jsonify({'auth_token': session['auth_token']}), 200)
    else:
        return make_response(jsonify({'error': 'Invalid password'}), 404)


@api.route('/logout', methods=['POST'])
@auth.login_required
def logout():
    _log.info("logout: %s" % request.json)
    session['auth_token'] = None
    logout_user()
    return make_response(jsonify({}), 204)


@api.route('/echo', methods=['GET'])
@auth.login_required
def echo():
    _log.info("echo: %s" % request.json)
    return make_response(jsonify({'data': request.json['data']}), 200)


# ===== List API =====


@api.route('/users/<int:user_id>/lists/<int:list_id>', methods=['GET'])
@auth.login_required
def get_list(user_id, list_id):
    if user_id != g.user.id:
        abort(403)
    tl = TaskList.query.filter_by(id=list_id).first()
    if not tl:
        return abort(404)
    else:
        return make_response(jsonify({'name': tl.name,
                                      'description': tl.description}), 200)


@api.route('/users/<int:user_id>/lists', methods=['POST'])
@auth.login_required
def create_list(user_id):
    if user_id != g.user.id:
        abort(403)
    if not request.json or 'name' not in request.json:
        abort(400)
    new_tl = TaskList(name=request.json.get('name'),
                      description=request.json.get('description', ""),
                      author_id=g.user.id)
    err = g.user.create_list(new_tl)
    if err:
        if "already exists" in err:
            abort(409, err)
        else:
            abort(500)

    response = jsonify({'list': url_for('api_1.get_list',
                                        user_id=g.user.id,
                                        list_id=new_tl.id)})
    return make_response(response, 201)


@api.route('/users/<int:user_id>/lists/<int:list_id>', methods=['PUT'])
@auth.login_required
def update_list(user_id, list_id):
    if user_id != g.user.id:
        abort(403)
    tl = TaskList.query.filter_by(id=list_id).first()
    if not tl:
        return abort(404)
    tl.name = request.json.get('name')
    tl.description = request.json.get('description')

    response = jsonify({'list': url_for('api_1.get_list',
                                         user_id=g.user.id,
                                         list_id=tl.id)})

    return make_response(response, 200)


@api.route('/users/<int:user_id>/lists/<int:list_id>', methods=['DELETE'])
@auth.login_required
def delete_list(user_id, list_id):
    if user_id != g.user.id:
        abort(403)
    tl = TaskList.query.filter_by(id=list_id).first()
    if not tl:
        return abort(404)
    err = g.user.delete_list(tl)
    if err:
        if 'User %s has no' % g.user.username in err:
            abort(404)
        else:
            abort(500)

    return make_response(jsonify({}), 200)


@api.route('/users/<int:user_id>/lists/<int:list_id>/subscribe', methods=['POST'])
@auth.login_required
def subscribe_on_list(user_id, list_id):
    pass


@api.route('/users/<int:user_id>/lists/<int:list_id>/unsubscribe', methods=['POST'])
@auth.login_required
def unsubscribe_from_list(user_id, list_id):
    pass


# ===== Task API =====

@api.route('/users/<int:user_id>/lists/<int:list_id>/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(user_id, list_id, task_id):
    pass


@api.route('/users/<int:user_id>/lists/<int:list_id>/tasks', methods=['POST'])
@auth.login_required
def create_task(user_id, list_id):
    pass


@api.route('/users/<int:user_id>/lists/<int:list_id>/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(user_id, list_id, task_id):
    pass


@api.route('/users/<int:user_id>/lists/<int:list_id>/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(user_id, list_id, task_id):
    pass