from flask import Blueprint

containers = Blueprint('containers', __name__)

from . import routes
