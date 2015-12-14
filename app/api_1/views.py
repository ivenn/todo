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


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


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
