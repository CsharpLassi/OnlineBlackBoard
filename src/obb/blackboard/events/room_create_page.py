from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from ..ext import namespace
from ..memory import MemoryLecturePage, lecture_page_memory, MemoryLecturePageData, \
    room_memory, MemoryUser, MemoryBlackboardRoom
from ..models import LecturePage, BlackboardRoom
from ...api import convert_from_socket, emit_success
from ...ext import socket, db


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomCreatePageRequestData:
    room_id: str
    parent_page_id: int
    direction: str
    move_to: bool = False


@dataclass
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomCreatePageResponseData:
    page: MemoryLecturePageData


@socket.on('room:create:page', namespace=namespace)
@convert_from_socket(RoomCreatePageRequestData)
def room_create_page(msg: RoomCreatePageRequestData,
                     session: MemoryUser = None, **kwargs):
    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)

    if not room:
        return

    mem_parent_page: MemoryLecturePage = lecture_page_memory.get(msg.parent_page_id)
    if not mem_parent_page:
        return

    page = mem_parent_page.model

    new_page = LecturePage.create(page.lecture)
    new_page.draw_width = room.model.draw_width
    new_page.draw_height = room.model.draw_height

    update_list = []

    update_list.append(page.id)

    # Todo: Left, Up, Down,
    if msg.direction == 'right':
        if page.right_page:
            right_page = page.right_page
            update_list.append(right_page.id)
            right_page.left_page = new_page
        new_page.left_page = page
        page.right_page = new_page

    db.session.add(new_page)
    db.session.commit()

    update_list.append(new_page.id)
    for page_id in update_list:
        update_page = lecture_page_memory.get(page_id, MemoryLecturePage(page_id))
        update_page.emit_update(room.id)

    update_list.append(new_page.id)

    if msg.move_to:
        session.current_page = new_page.id
        session.emit_self(changes=['currentPage'])

    return
