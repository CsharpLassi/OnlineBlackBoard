import random
import string

from .server_models import BlackboardRoom, UserSessions
from ..tools.MemDb import MemDb

namespace = '/blackboard'
room_db = MemDb[str, BlackboardRoom]()
user_db = MemDb[str, UserSessions]()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def check_rooms():
    room: BlackboardRoom
    for room_id, room in room_db.items():
        if len(room.users) == 0:
            room_db.pop(room_id)
