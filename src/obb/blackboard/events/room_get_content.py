from dataclasses import dataclass
from typing import List

from dataclasses_json import LetterCase, dataclass_json

from flask import escape

from obb.api import convert_from_socket, emit_success, emit_error
from obb.ext import socket
from ..ext import namespace
from ..memory import lecture_page_memory, MemoryLecturePage
from ..models import LecturePage


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetContentRequestData:
    page_id: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetContentResponse:
    page_id: int
    text: str
    markdown: str


@socket.on('room:get:content', namespace=namespace)
@convert_from_socket(RoomGetContentRequestData)
def room_get_content(msg_list: List[RoomGetContentRequestData], **kwargs):
    result = list()
    for msg in msg_list:
        page = LecturePage.get(msg.page_id)
        if not page:
            emit_error('page not found')
            continue
        new_page = MemoryLecturePage(page.id)
        mem_page: MemoryLecturePage = lecture_page_memory.get(msg.page_id, new_page)

        result.append(RoomGetContentResponse(
            page_id=mem_page.id,
            text=mem_page.markdown,
            markdown=escape(mem_page.markdown)

        ))

    emit_success('room:get:content', result)
