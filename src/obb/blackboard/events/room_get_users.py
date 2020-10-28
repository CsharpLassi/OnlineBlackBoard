from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json, LetterCase

from obb.api import convert_from_socket, emit_error, emit_success
from obb.blackboard.ext import namespace
from obb.blackboard.memory import (
    MemorySessionUser,
    room_memory,
    user_session_memory,
    MemorySessionUserData,
    MemoryBlackboardRoom,
)
from obb.ext import socket


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetUserRequestData:
    room_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RoomGetUserResponseData:
    users: List[MemorySessionUserData]


@socket.on("room:get:users", namespace=namespace)
@convert_from_socket(RoomGetUserRequestData)
def room_get_users(msg: RoomGetUserRequestData, **kwargs):
    room: MemoryBlackboardRoom = room_memory.get(msg.room_id)

    if not room:
        emit_error("not allowed")
        return

    joined_user = list()
    user: MemorySessionUser
    for _, user in user_session_memory.items():
        if user.sid in room.users:
            joined_user.append(user.get_data())
    emit_success("room:get:users", RoomGetUserResponseData(users=joined_user))
