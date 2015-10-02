from itsdangerous import URLSafeTimedSerializer

from app import app
from logging import getLogger

_LOGGER = getLogger(__name__)


def generate_confiramation_token(name):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(name, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expire_time=86400):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    name = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expire_time)
    return name