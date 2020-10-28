from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from obb.api import convert_from_socket
from obb.ext import socket
from ..ext import namespace
from ..memory import (
    MemorySessionUser,
    MemorySessionUserData,
    MemoryLecturePage,
    lecture_page_memory,
)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomMoveToPageRequestData:
    page_id: str


@dataclass_json
@dataclass
class RoomMoveToPageResponseData:
    user: MemorySessionUserData


@socket.on("room:moveTo:page", namespace=namespace)
@convert_from_socket(RoomMoveToPageRequestData)
def room_moveto_page(
    msg: RoomMoveToPageRequestData, session: MemorySessionUser = None, **kwargs
):
    if not msg.page_id:
        return

    page: MemoryLecturePage = lecture_page_memory.get(
        msg.page_id, MemoryLecturePage(msg.page_id)
    )
    if page is None:
        return
    session.current_page = page.id

    session.emit_self(changes=["currentPage"])
