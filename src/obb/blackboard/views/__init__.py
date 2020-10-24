from flask import Blueprint
from ..ext import namespace

bp = Blueprint('blackboard', __name__, url_prefix=namespace)

from . import home

from . import room
from . import room_link

from . import session
