from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase
from flask import request, current_app

from obb.ext import socket
from ..ext import namespace
from ..memory import user_memory, MemoryUser, room_memory, MemoryBlackboardRoom
from ...api import emit_success


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserLeaveResponseData:
    session_id: str


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    sid = request.sid
    current_app.logger.debug(f'Connect Socket: {sid}')


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    sid = request.sid
    current_app.logger.debug(f'Disconnect Socket: {sid}')
    user: MemoryUser = user_memory.find(lambda k, u: u.socket_id == sid)

    if user is None:
        return

    room: MemoryBlackboardRoom = room_memory.get(user.current_room)

    if room:
        room.users.remove(user.session_id)

    emit_success('room:leave:user', UserLeaveResponseData(
        session_id=user.session_id
    ), room=user.current_room)
