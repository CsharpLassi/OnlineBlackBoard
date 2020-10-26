from __future__ import annotations

from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from obb.users.models import User, UserData
from obb.tools import id_generator


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemoryUserData:
    base: UserData
    session_id: str
    current_page: int
    mode: str
    allow_draw: bool
    allow_new_page: bool


class MemoryUser:
    def __init__(self, sid: str, id: int):
        self.sid = sid
        self.id = id

        self.session_id = id_generator(6)
        self.current_page = 0

        self.mode: str = 'blackboard'
        self.allow_draw: bool = False
        self.allow_new_page: bool = False

    def get_data(self) -> MemoryUserData:
        user = self.model

        user_data = UserData() if user is None else user.get_data()
        return MemoryUserData(
            base=user_data,
            session_id=self.session_id,
            current_page=self.current_page,
            mode=self.mode,
            allow_draw=self.allow_draw,
            allow_new_page=self.allow_new_page,
        )

    def emit_self(self):
        from obb.api import emit_success
        emit_success('self:update', self.get_data(), sid=self.sid)

    @property
    def model(self) -> User:
        return User.get(self.id)
