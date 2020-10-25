from flask import Blueprint
from ..ext import namespace

bp = Blueprint('blackboard', __name__, url_prefix=namespace)

# Home
from . import home

# Rooms
from . import room
from . import room_link

# Sessions
from . import session

# Lecturs
from . import lecture
