from flask import jsonify, make_response, session, request, g
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask_httpauth import HTTPBasicAuth

from app.api_1 import api_1 as api
from app.models import User, Task, TaskList

from logging import getLogger

_LOGGER = getLogger("restV1_" + __name__)

auth = HTTPBasicAuth()

@api.before_request
def before_request():
    g.user = current_user

@auth.verify_password
def verify_password(token, username=None):
    "Username are not used in this case, becouse we are use token based authentication"
    user = User.verify_auth_token(token)
    session_token = session['auth_token'] if 'auth_token' in session else None
    if session_token and session_token == token and user:
        return True
    return False


@api.route('/login', methods=['POST'])
def login():
    if not request.json or 'username' not in request.json or 'password' not in request.json:
        return make_response(jsonify({'error': 'wrong request'}), 404)

    user = User.query.filter_by(username=request.json['username']).first()
    if user.verify_password(request.json['password']):
        login_user(user)
        if not user.confirmed:
            return make_response(jsonify({'error': 'You registration is not confirmed'}), 404)
        session['auth_token'] = g.user.generate_auth_token().decode('ascii')
        return make_response(jsonify({'auth_token': session['auth_token']}), 200)
    else:
        return make_response(jsonify({'error': 'Invalid password'}), 404)


@api.route('/logout', methods=['POST'])
@auth.login_required
def logout():
    session['auth_token'] = None
    logout_user()
    return make_response(jsonify({}), 204)


@api.route('/test', methods=['POST'])
@auth.login_required
def test():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })