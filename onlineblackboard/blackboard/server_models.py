from hashlib import md5
from typing import Dict, Optional
from .functions import id_generator
from .messages import RoomData, UserData, RoomUpdateContentData


class BlackboardRoomSession:
    def __init__(self, room_name: str):
        self.room_name: str = room_name
        self.room_id: str = self.get_hash(room_name)

        self.users: Dict[str, UserSessions] = dict()

        self.last_data: Optional[RoomUpdateContentData] = None

    @staticmethod
    def get_hash(value: str) -> str:
        return md5(value.encode()).hexdigest()

    def has_users(self) -> bool:
        return len(self.users) > 0

    def to_data(self) -> RoomData:
        return RoomData(room_id=self.room_id,
                        room_name=self.room_name)

    def to_dict(self) -> dict:
        return self.to_data().to_dict()


class UserSessions:
    def __init__(self, sid: str, username: str = "Generic User"):
        self.user_id = id_generator(size=12)
        self.sid: str = sid
        self.username: str = username
        self.rooms: Dict[str, BlackboardRoomSession] = dict()

    def to_data(self) -> UserData:
        return UserData(user_id=self.user_id,
                        username=self.username)

    def to_dict(self) -> dict:
        return self.to_data().to_dict()
