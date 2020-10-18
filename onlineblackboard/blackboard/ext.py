import flask
from werkzeug.local import LocalProxy

from .server_models import BlackboardRoomSession, UserSessions
from ..tools.MemDb import MemDb

namespace = '/blackboard'
room_db = MemDb[str, BlackboardRoomSession]()

user_db = MemDb[str, UserSessions]()


def check_rooms():
    room: BlackboardRoomSession
    for room_id, room in room_db.items():
        if len(room.users) == 0:
            room_db.pop(room_id)
