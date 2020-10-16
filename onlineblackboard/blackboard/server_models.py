from typing import Dict


class BlackboardRoom:
    def __init__(self, room_id: str):
        self.room_id: str = room_id
        self.users: Dict[str, UserSessions] = dict()


class UserSessions:
    def __init__(self, sid: str):
        self.sid = sid
        self.rooms: Dict[str, BlackboardRoom] = dict()

    def connect(self):
        return

    def disconnect(self, disconnect_rooms: bool = True):
        if disconnect_rooms:
            for room_id, room in self.rooms.items():
                room.users.pop(self.sid)
