from flask import Blueprint

api_1 = Blueprint('api_1', __name__)

from app.api_1 import views
