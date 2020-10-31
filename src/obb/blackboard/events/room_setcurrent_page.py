from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from obb.api import convert_from_socket, emit_error
from obb.ext import socket, db
from ..ext import namespace
from ..memory import (
    lecture_page_memory,
    MemorySessionUser,
    MemoryLecturePage,
    MemoryBlackboardRoom,
    room_memory,
)
from ..models import Lecture


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SetCurrentPageRequestData:
    room_id: str
    page_id: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class SetCurrentPageResponse:
    pass


@socket.on("room:setCurrent:page", namespace=namespace)
@convert_from_socket(SetCurrentPageRequestData)
def room_get_content(
    msg: SetCurrentPageRequestData, session: MemorySessionUser = None, **kwargs
):
    if not session.allow_new_page:
        emit_error("action is not allowed")
        return

    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)
    if not room:
        return

    page: MemoryLecturePage = lecture_page_memory.get(msg.page_id)

    lecture: Lecture = page.model.lecture

    old_current_page: MemoryLecturePage = lecture_page_memory.get(
        lecture.current_page.id
    )

    lecture.current_page_id = msg.page_id

    db.session.commit()

    page.emit_update(room.id)
    if old_current_page:
        old_current_page.emit_update(room.id)
