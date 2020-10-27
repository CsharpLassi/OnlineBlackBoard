from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase
from flask import request
from flask_socketio import join_room

from obb.api import convert_from_socket, emit_error, emit_success
from obb.ext import socket
from ..ext import namespace
from ..memory import room_memory, MemoryBlackboardRoom, MemoryBlackboardRoomData, \
    user_memory, MemoryUser, MemoryUserData
from ..models import BlackboardRoom
from ...users.models import User


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomJoinRequestData:
    room_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomJoinSelfResponseData:
    sid: str
    room: MemoryBlackboardRoomData
    user: MemoryUserData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomJoinUserResponseData:
    room_id: str
    user: MemoryUserData


@socket.on('room:join', namespace=namespace)
@convert_from_socket(RoomJoinRequestData)
def join(msg: RoomJoinRequestData, user: User = None, sid: str = None, **kwargs):
    assert sid

    room = BlackboardRoom.get(msg.room_id)
    if not room:
        return emit_error('you cannot join this room')

    l_session = room.get_current_lecture_session()
    if not l_session:
        return emit_error('room is closed')

    lecture = l_session.lecture

    memory_room = room_memory.get(room.id, MemoryBlackboardRoom(room.id))
    memory_user = user_memory.get(sid, MemoryUser(sid, 0 if not user else user.id))
    memory_user.current_page = lecture.current_page_id or lecture.current_page_id or 0

    join_room(room.id)
    memory_user.current_room = room.id
    memory_user.socket_id = request.sid

    memory_room.users.add(memory_user.session_id)

    emit_success('room:join:self', RoomJoinSelfResponseData(
        sid=sid,
        room=memory_room.get_data(),
        user=memory_user.get_data(),
    ))

    emit_success('room:join:user', RoomJoinUserResponseData(
        room_id=room.id,
        user=memory_user.get_data(),
    ), room=room.id)
