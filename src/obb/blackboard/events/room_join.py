from dataclasses import dataclass

from flask import request
from flask_socketio import join_room, emit

from obb.ext import socket
from obb.users.models import User

from ..components.session_manager import BlackBoardSession
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import UserData, RoomData
from ..models import BlackboardRoom


@dataclass
class JoinRequestMessage(BaseRequestMessage):
    pass


@dataclass
class UserJoinedResponse(BaseResponseMessage):
    user: UserData
    room: RoomData


@socket.on('room:join', namespace=namespace)
@convert(JoinRequestMessage)
@event_login_required
def join(msg: JoinRequestMessage,
         room: BlackboardRoom = None):
    sid = request.sid
    session: BlackBoardSession = bb_session_manager.get(msg.session.session_id)

    user: User = session.get_user()
    if not room.can_join(user=user):
        return

    join_room(room.id)
    bb_session_manager.join(sid, msg.session.session_id)

    response_data = UserJoinedResponse(
        user=session.session_user_data,
        room=session.session_room_data)
    response_data_dict = response_data.to_dict()

    emit('room:user:join', response_data_dict, room=room.id)
    emit('room:join', response_data_dict)
