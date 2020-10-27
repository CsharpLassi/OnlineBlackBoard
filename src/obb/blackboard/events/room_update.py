from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import socket, db
from ..ext import namespace
from ..forms.room import RoomSettingsForm
from ..memory import (
    MemoryBlackboardRoomData,
    room_memory,
    MemoryBlackboardRoom,
    lecture_page_memory,
    MemoryLecturePage,
)
from ...api import convert_from_socket, emit_success
from ...tools.forms import get_form_data_from_dict


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomUpdateRequestData:
    room_id: str
    data: List[dict]

    page_id: int = None


@dataclass()
class RoomUpdateResponseData:
    room: MemoryBlackboardRoomData


@socket.on("room:update", namespace=namespace)
@convert_from_socket(RoomUpdateRequestData)
def room_update(msg: RoomUpdateRequestData, **kwargs):
    form_data = get_form_data_from_dict(msg.data)
    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)

    room_settings = RoomSettingsForm(form_data)
    if room_settings.validate() and room:

        room_settings.write_data(room.model)

        db.session.commit()

        emit_success(
            "room:update", RoomUpdateResponseData(room=room.get_data()), room=room.id
        )

        page: MemoryLecturePage = lecture_page_memory.get(msg.page_id)

        if page:
            page.model.draw_width = room_settings.draw_width.data
            page.model.draw_height = room_settings.draw_height.data
            db.session.commit()

            page.emit_update(room.id, ["drawWidth", "drawHeight"])

    return
