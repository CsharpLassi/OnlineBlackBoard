from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from dataclasses_json import LetterCase, dataclass_json

from obb.blackboard.datas import StrokeData
from obb.users.models import User, UserData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemorySessionUserData:
    base: UserData
    session_id: str
    current_room: str
    current_page: int
    mode: str
    allow_draw: bool
    allow_new_page: bool


class MemorySessionUser:
    def __init__(self, sid: str, id: int = None):
        self.sid = sid
        self.id = id
        self.socket_id = None

        self.current_room: str = ""
        self.current_page = 0

        self.mode: str = "blackboard"
        self.allow_draw: bool = False
        self.allow_new_page: bool = False

        self.strokes: Dict[int, List[StrokeData]] = dict()

    @property
    def model(self) -> User:
        return User.get(self.id)

    def get_data(self) -> MemorySessionUserData:
        user = self.model

        user_data = UserData() if user is None else user.get_data()
        return MemorySessionUserData(
            base=user_data,
            session_id=self.sid,
            current_room=self.current_room,
            current_page=self.current_page,
            mode=self.mode,
            allow_draw=self.allow_draw,
            allow_new_page=self.allow_new_page,
        )

    def emit_self(self, changes: list = None):
        from obb.api import emit_success
        from ..events.global_message import UserUpdatedEvent

        if not self.socket_id:
            return

        emit_success(
            "self:update",
            UserUpdatedEvent(
                user=self.get_data(),
                all=not list,
                changes=list() if changes is None else changes,
            ),
            room=self.socket_id,
        )

    def clear_temp_data(self):
        pass
