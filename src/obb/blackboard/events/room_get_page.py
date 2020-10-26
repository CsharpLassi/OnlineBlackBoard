from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from ..ext import namespace
from ..memory import MemoryLecturePage, lecture_page_memory, MemoryLecturePageData
from ...api import convert_from_socket, emit_success
from ...ext import socket


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetPageRequestData:
    page_id: int


@dataclass
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetPageResponseData:
    page: MemoryLecturePageData


@socket.on('room:get:page', namespace=namespace)
@convert_from_socket(RoomGetPageRequestData)
def room_get_page(msg: RoomGetPageRequestData, **kwargs):
    page: MemoryLecturePage = lecture_page_memory.get(msg.page_id)

    if not page:
        return

    emit_success('room:get:page', RoomGetPageResponseData(
        page=page.get_data()
    ))
