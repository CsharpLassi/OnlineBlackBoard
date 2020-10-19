from __future__ import annotations

import dataclasses
from typing import Optional

import jwt
from dataclasses import dataclass

from flask import current_app
from flask_login import current_user

from ..models import BlackboardRoom

from ..messages.datas import UserData, RoomData

from obb.tools import id_generator
from obb.tools.MemDb import MemDb
from obb.tools.dataclasses import dataclass_from_dict
from obb.users.models import User


@dataclass
class BlackBoardSessionToken:
    session_id: str

    def encode(self) -> str:
        session_dict = dataclasses.asdict(self)
        return jwt.encode(session_dict, current_app.secret_key, 'HS256')

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

    def get_token(self) -> BlackBoardSessionToken:
        return BlackBoardSessionToken(session_id=self.session_id)

    def to_token_string(self) -> str:
        return self.get_token().encode()


class BlackBoardSessionManager:
    def __init__(self):
        self.__db = MemDb[str, BlackBoardSession]()
        self.__sid_to_session_db = MemDb[str, str]()

    def create_session(self, room_id: str, user: User = None) -> BlackBoardSession:
        if user is None:
            user = current_user

        room = BlackboardRoom.get(room_id)

        user_data = UserData(
            user_id=id_generator(),
            username=user.username
        )

        room_data = RoomData(
            room_id=room_id,
            room_name=room.name
        )

        session = BlackBoardSession(
            session_id=id_generator(),
            room_id=room_id,
            user_id=user.id,
            session_user_data=user_data,
            session_room_data=room_data,
        )

        self.__db.add(session.session_id, session)

        return session

    def join(self, sid: str, session_id: str):
        if not self.__db.exist(session_id):
            return
        self.__sid_to_session_db.add(sid, session_id)

    def leave(self, sid: str) -> Optional[BlackBoardSession]:
        session_id = self.__sid_to_session_db.pop(sid)
        if not session_id:
            return
        session = self.__db.pop(session_id)
        return session

    def get(self, session_id: str) -> Optional[BlackBoardSession]:
        return self.__db.get(session_id)
