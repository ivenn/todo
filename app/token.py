from itsdangerous import URLSafeTimedSerializer

from flask import current_app
from logging import getLogger

_log = getLogger(__name__)


def generate_confiramation_token(name):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(name, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expire_time=86400):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    name = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expire_time)
    return name