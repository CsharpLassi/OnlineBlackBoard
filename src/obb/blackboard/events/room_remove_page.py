from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from ..ext import namespace
from ..memory import (
    MemoryLecturePage,
    lecture_page_memory,
    room_memory,
    MemorySessionUser,
    MemoryBlackboardRoom,
)
from ...api import convert_from_socket, emit_error, emit_success
from ...ext import socket, db


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomRemovePageRequestData:
    room_id: str
    page_id: int


@dataclass
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomRemovePageResponseData:
    page_id: int
    move_to: int


@socket.on("room:remove:page", namespace=namespace)
@convert_from_socket(RoomRemovePageRequestData)
def room_remove_page(
    msg: RoomRemovePageRequestData, session: MemorySessionUser = None, **kwargs
):
    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)

    if not session.allow_new_page:
        emit_error("you cannot create new pages")
        return

    if not room:
        return

    mem_page: MemoryLecturePage = lecture_page_memory.get(msg.page_id)
    if not mem_page:
        return

    page = mem_page.model

    if not page.prev_page:
        return

    prev_page = page.prev_page
    next_pages = list(page.next_pages)

    update_list = []
    update_list.append(page.prev_page.id)
    update_list.append(page.id)

    for next_page in next_pages:
        next_page.prev_page = prev_page
        update_list.append(next_page.id)

    page.prev_page = None

    if page.lecture.current_page == page.id:
        page.lecture.current_page = None

    db.session.commit()

    for page_id in update_list:
        update_page = lecture_page_memory.get(page_id, MemoryLecturePage(page_id))
        update_page.emit_update(room.id)

    emit_success(
        "room:remove:page",
        RoomRemovePageResponseData(page_id=page.id, move_to=prev_page.id),
    )
