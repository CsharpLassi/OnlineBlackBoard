from dataclasses import dataclass

from flask import request, current_app
from flask_socketio import emit

from obb.ext import socket
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseResponseMessage
from ..messages.datas import UserData, RoomData


@dataclass
class UserLeaveResponse(BaseResponseMessage):
    user: UserData
    room: RoomData


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    sid = request.sid
    current_app.logger.debug(f'Connect Socket: {sid}')


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    sid = request.sid
    current_app.logger.debug(f'Disconnect Socket: {sid}')

    session = bb_session_manager.leave(sid)
    if session:
        leave_data = UserLeaveResponse(
            user=session.session_user_data,
            room=session.session_room_data
        )

        emit('room:leave:user', leave_data.to_dict(), room=session.room_id)
