from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import datetime
from typing import Optional

import jwt
from flask import current_app
from flask_login import current_user

from obb.tools import id_generator
from obb.tools.MemDb import MemDb
from obb.tools.dataclasses import dataclass_from_dict
from obb.users.models import User
from ..messages.datas import UserData, RoomData
from ..models import BlackboardRoom


def calc_exp(minutes: float = 0) -> datetime.datetime:
    date = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    return date


@dataclass
class BlackBoardSessionToken:
    session_id: str
    exp: datetime.datetime = dataclasses.field(
        default_factory=lambda: calc_exp(minutes=120))

    def is_expired(self) -> bool:
        return datetime.datetime.utcnow() > self.exp

    def encode(self) -> str:
        session_dict = dataclasses.asdict(self)
        return jwt.encode(session_dict, current_app.secret_key, 'HS256').decode('UTF-8')

    @staticmethod
    def decode(token: str) -> BlackBoardSessionToken:
        session_dict = jwt.decode(token, current_app.secret_key, algorithms=['HS256'])
        return dataclass_from_dict(BlackBoardSessionToken, session_dict)


@dataclass
class BlackBoardSession:
    session_id: str
    room_id: str
    user_id: int
    session_user_data: UserData
    session_room_data: RoomData
    exp: datetime.datetime = dataclasses.field(
        default_factory=lambda: calc_exp(minutes=120))

    def refresh(self):
        self.exp = calc_exp(minutes=120)

    def is_expired(self) -> bool:
        return datetime.datetime.utcnow() > self.exp

    def get_token(self) -> BlackBoardSessionToken:
        return BlackBoardSessionToken(session_id=self.session_id)

    def to_token_string(self) -> str:
        return self.get_token().encode()

    def get_user(self) -> Optional[User]:
        return User.get(self.user_id)


class BlackBoardSessionManager:
    def __init__(self):
        self.__db = MemDb[str, BlackBoardSession]()
        self.__users = MemDb[str, UserData]()
        self.__sid_to_session_db = MemDb[str, str]()
        self.__rooms = MemDb[str, RoomData]()

    def create_session(self, room_id: str, user: User = None,
                       mode: str = 'default') -> BlackBoardSession:
        if user is None and current_user.is_authenticated:
            user = current_user
        elif not current_user.is_authenticated:
            pass  # Todo: raise exception

        room = BlackboardRoom.get(room_id)

        user_data = UserData(
            user_id=id_generator(),
            username='Guest' if not user else user.username,
            creator=(room.creator_id == user.id if user else 0),
            mode=mode,
        )
        self.__users.add(user_data.user_id, user_data)

        room_data = self.__rooms.get(room_id, RoomData(
            room_id=room_id,
            room_name=room.name
        ))

        session = BlackBoardSession(
            session_id=id_generator(),
            room_id=room_id,
            user_id=0 if not user else user.id,
            session_user_data=user_data,
            session_room_data=room_data,
        )

        self.__db.add(session.session_id, session)

        return session

    def join(self, sid: str, session_id: str):
        session = self.get(session_id)
        if not session:
            return
        self.__sid_to_session_db.add(sid, session_id)

        room_data: Optional[RoomData] = self.__rooms.get(session.room_id)
        room_data.users[session.session_user_data.user_id] = session.session_user_data

        return

    def leave(self, sid: str) -> Optional[BlackBoardSession]:
        session_id = self.__sid_to_session_db.pop(sid)
        if not session_id:
            return

        session: Optional[BlackBoardSession] = self.__db.get(session_id)
        room: Optional[RoomData]
        if session and (room := self.__rooms.get(session.room_id)):
            user_data = room.users.pop(session.session_user_data.user_id)
            pass
        return session

    def get(self, session_id: str) -> Optional[BlackBoardSession]:
        return self.__db.get(session_id)

    def get_user(self, user_id: str) -> Optional[UserData]:
        return self.__users.get(user_id)
