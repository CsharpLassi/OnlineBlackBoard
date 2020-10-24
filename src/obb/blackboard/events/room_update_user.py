from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import UserData
from ..models import BlackboardRoom


@dataclass
class RoomUpdateUserRequestMessage(BaseRequestMessage):
    user_id: str
    allow_draw: bool = None


@dataclass()
class RoomUpdateUserResponseMessage(BaseResponseMessage):
    user: UserData


@socket.on('room:update:user', namespace=namespace)
@convert(RoomUpdateUserRequestMessage)
@event_login_required
def blackboard_room_update_user(msg: RoomUpdateUserRequestMessage,
                                room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)
    updated_user = bb_session_manager.get_user(msg.user_id)

    update_counter = 0

    allow_change = session.session_user_data.creator
    if allow_change:
        if updated_user and msg.allow_draw is not None:
            updated_user.allow_draw = msg.allow_draw
            update_counter += 1

    response_data = RoomUpdateUserResponseMessage(
        user=updated_user,
    )
    if update_counter > 0:
        emit('room:update:user', response_data.to_dict(), room=room.id)
    else:
        emit('room:update:user', response_data.to_dict())
