from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase
from flask import escape

from obb.ext import socket, db
from .global_message import NewLecturePageEvent
from ..ext import namespace
from ..memory import (
    room_memory,
    MemoryBlackboardRoom,
    lecture_page_memory,
    MemoryLecturePage,
    MemoryUser,
)
from ..models import LecturePage
from ...api import convert_from_socket, emit_error, emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomUpdateContentRequest:
    room_id: int
    text: str

    page_id: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomUpdateContentResponse:
    room_id: str
    page_id: int
    creator_id: str
    text: str
    markdown: str


@socket.on("room:update:content", namespace=namespace)
@convert_from_socket(RoomUpdateContentRequest)
def room_update_content(msg: RoomUpdateContentRequest, session: MemoryUser, **kwargs):
    assert session

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
    page.markdown = msg.text

    emit_success(
        "room:update:content",
        RoomUpdateContentResponse(
            room_id=room.id,
            page_id=page.id,
            creator_id=session.sid,
            text=page.markdown,
            markdown=escape(page.markdown),
        ),
        room=room.id,
    )

    # Save
    page.save_markdown()
