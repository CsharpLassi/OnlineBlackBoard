from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from ..ext import namespace
from ..memory import (
    MemoryLecturePage,
    lecture_page_memory,
    MemoryLecturePageData,
    room_memory,
    MemorySessionUser,
    MemoryBlackboardRoom,
)
from ..models import LecturePage
from ...api import convert_from_socket, emit_error
from ...ext import socket, db


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomCreatePageRequestData:
    room_id: str
    parent_page_id: int
    move_to: bool = False


@dataclass
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomCreatePageResponseData:
    page: MemoryLecturePageData


@socket.on("room:create:page", namespace=namespace)
@convert_from_socket(RoomCreatePageRequestData)
def room_create_page(
    msg: RoomCreatePageRequestData, session: MemorySessionUser = None, **kwargs
):
    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)

    if not session.allow_new_page:
        emit_error("you cannot create new pages")
        return

    if not room:
        return

    mem_parent_page: MemoryLecturePage = lecture_page_memory.get(msg.parent_page_id)
    if not mem_parent_page:
        return

    page = mem_parent_page.model

    new_page = LecturePage.create(page.lecture)
    new_page.draw_width = room.model.draw_width
    new_page.draw_height = room.model.draw_height
    new_page.prev_page = page

    update_list = []

    update_list.append(page.id)

    if len(page.next_pages) > 0:
        next_page: LecturePage = page.next_pages[0]
        next_page.prev_page = new_page
        update_list.append(next_page.id)

    db.session.add(new_page)
    db.session.commit()
    update_list.append(new_page.id)

    for page_id in update_list:
        update_page = lecture_page_memory.get(page_id, MemoryLecturePage(page_id))
        update_page.emit_update(room.id)

    if msg.move_to:
        session.current_page = new_page.id
        session.emit_self(changes=["currentPage"])

    return
