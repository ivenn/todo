from flask import Blueprint

rest = Blueprint('rest', __name__)

from app.rest import views
