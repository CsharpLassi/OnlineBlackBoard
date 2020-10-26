from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import socket
from ..ext import namespace
from ..memory import MemoryLecturePage, lecture_page_memory
from ..messages.datas import StrokeData
from ..models import LecturePage
from ...api import convert_from_socket, emit_error, emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetSketchRequestData:
    page_id: int = 0


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetSketchResponseData:
    page_id: int
    strokes: List[StrokeData] = field(default_factory=list)


@socket.on('room:get:sketch', namespace=namespace)
@convert_from_socket(RoomGetSketchRequestData)
def room_get_sketch(msg_list: List[RoomGetSketchRequestData], **kwargs):
    result = list()
    for msg in msg_list:
        page = LecturePage.get(msg.page_id)
        if not page:
            emit_error('page not found')
            continue

        new_page = MemoryLecturePage(page.id)
        mem_page: MemoryLecturePage = lecture_page_memory.get(msg.page_id, new_page)

        result.append(RoomGetSketchResponseData(
            page_id=mem_page.id,
            strokes=mem_page.strokes,

        ))

    emit_success('room:get:sketch', result)
