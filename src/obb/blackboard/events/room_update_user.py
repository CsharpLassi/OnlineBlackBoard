from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import socket
from ..ext import namespace
from ..memory import user_memory, MemoryUser, MemoryUserData
from ...api import convert_from_socket, emit_error, emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomUpdateUserRequest:
    session_id: str
    allow_draw: bool = None
    allow_new_page: bool = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomUpdateUserResponse:
    user: MemoryUserData


@socket.on("room:update:user", namespace=namespace)
@convert_from_socket(RoomUpdateUserRequest)
def room_update_user(msg: RoomUpdateUserRequest, session: MemoryUser, **kwargs):
    assert session

    update_user: MemoryUser = user_memory.find(
        lambda k, u: u.session_id == msg.session_id
    )

    if not update_user:
        emit_error("not allowed")

    change_list = []

    if msg.allow_draw is not None:
        update_user.allow_draw = msg.allow_draw
        change_list.append("allowDraw")

    if msg.allow_new_page is not None:
        update_user.allow_new_page = msg.allow_new_page
        change_list.append("allowNewPage")

    response = RoomUpdateUserResponse(user=update_user.get_data())

    if len(change_list) > 0:
        update_user.emit_self(changes=change_list)
        emit_success("room:update:user", response, room=session.current_room)
    else:
        emit_success("room:update:user", response)
