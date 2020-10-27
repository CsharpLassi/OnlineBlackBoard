from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import socket, db
from .global_message import NewLecturePageEvent
from ..ext import namespace
from ..memory import (
    MemoryUser,
    MemoryBlackboardRoom,
    room_memory,
    MemoryLecturePage,
    lecture_page_memory,
)
from ..models import LecturePage
from ...api import convert_from_socket, emit_error, emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomClearSketchRequestData:
    room_id: int
    mode: str

    page_id: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomClearSketchResponseData:
    room_id: str
    page_id: int
    creator_id: int


@socket.on("room:clear:sketch", namespace=namespace)
@convert_from_socket(RoomClearSketchRequestData)
def room_clear_sketch(msg: RoomClearSketchRequestData, session: MemoryUser, **kwargs):
    assert session

    # Todo: Add User Function
    if msg.mode != "global":
        return

    if not session.allow_draw:
        return

    room: Optional[MemoryBlackboardRoom] = room_memory.get(msg.room_id)
    if not room:
        emit_error("room not found")
        return

    l_session = room.model.get_current_lecture_session()
    if not l_session:
        emit_error("room is closed")
        return
    lecture = l_session.lecture

    page_id = msg.page_id or lecture.current_page.id

    # Create New Page
    if page_id is None:
        pass  # Todo: Exception

    page = lecture_page_memory.get(page_id, MemoryLecturePage(page_id))
    page.strokes.clear()

    emit_success(
        "room:clear:sketch",
        RoomClearSketchResponseData(
            room_id=room.id, page_id=page.id, creator_id=session.session_id
        ),
        room=room.id,
    )

    page.save_strokes()
