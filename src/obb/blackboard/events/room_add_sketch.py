from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import socket, db
from .global_message import NewLecturePageEvent
from ..datas import StrokeData
from ..ext import namespace
from ..memory import (
    MemorySessionUser,
    MemoryBlackboardRoom,
    room_memory,
    MemoryLecturePage,
    lecture_page_memory,
)
from ..models import LecturePage
from ...api import convert_from_socket, emit_error, emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomAddSketchRequestData:
    room_id: int
    mode: str
    stroke: StrokeData

    page_id: Optional[int] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomAddSketchResponseData:
    room_id: str
    page_id: int
    creator_id: str
    stroke: StrokeData


@socket.on("room:add:sketch", namespace=namespace)
@convert_from_socket(RoomAddSketchRequestData)
def room_update_sketch(
    msg: RoomAddSketchRequestData, session: MemorySessionUser, **kwargs
):
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
    page.strokes.append(msg.stroke)

    emit_success(
        "room:add:sketch",
        RoomAddSketchResponseData(
            room_id=room.id, page_id=page.id, creator_id=session.sid, stroke=msg.stroke
        ),
        room=room.id,
        include_self=False,
    )

    page.save_strokes()
