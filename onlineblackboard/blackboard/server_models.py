from typing import Dict
from .functions import id_generator


class BlackboardRoom:
    def __init__(self, room_id: str):
        self.room_id: str = room_id
        self.users: Dict[str, UserSessions] = dict()


class UserSessions:
    def __init__(self, sid: str, username: str = "Generic User"):
        self.user_id = id_generator(size=12)
        self.sid: str = sid
        self.username: str = username
        self.rooms: Dict[str, BlackboardRoom] = dict()

    def get_msg_data(self) -> dict:
        return {
            'user_id': self.user_id,
            'username': self.username,
        }
