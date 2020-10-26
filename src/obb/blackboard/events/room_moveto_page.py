from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from obb.api import convert_from_socket
from obb.ext import socket
from ..ext import namespace
from ..memory import MemoryUser, MemoryUserData, MemoryLecturePage, lecture_page_memory


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomMoveToPageRequestData:
    page_id: str


@dataclass_json
@dataclass
class RoomMoveToPageResponseData:
    user: MemoryUserData


@socket.on('room:moveTo:page', namespace=namespace)
@convert_from_socket(RoomMoveToPageRequestData)
def room_moveto_page(msg: RoomMoveToPageRequestData,
                     session: MemoryUser = None, **kwargs):
    page: MemoryLecturePage = lecture_page_memory.get(msg.page_id)
    session.current_page = page.id

    session.emit_self()
