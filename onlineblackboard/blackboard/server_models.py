from typing import Dict, Optional

from .functions import id_generator
from .messages import RoomData, UserData, RoomUpdateContentData
from .models import BlackboardRoom


class BlackboardRoomSession:
    def __init__(self, db_room: BlackboardRoom):
        self.room_id = db_room.id
        self.room_name: str = db_room.name
        self.__db_room = db_room

        self.users: Dict[str, UserSessions] = dict()

        self.last_data: Optional[RoomUpdateContentData] = None

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
        self.rooms: Dict[int, BlackboardRoomSession] = dict()

    def to_data(self) -> UserData:
        return UserData(user_id=self.user_id,
                        username=self.username)

    def to_dict(self) -> dict:
        return self.to_data().to_dict()
