from typing import Optional

from flask import request, current_app, escape, url_for
from flask_login import current_user
from flask_socketio import emit, join_room

from .ext import namespace, room_db, user_db
from .server_models import UserSessions, BlackboardRoom
from .decorators import convert
from .messages import *
from ..ext import socket


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    sid = request.sid
    current_app.logger.debug(f'Connect Socket: {sid}')

    user: UserSessions = user_db.get(sid, UserSessions(sid))

    if current_user and current_user.is_authenticated:
        user.username = current_user.username


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    sid = request.sid
    current_app.logger.debug(f'Disconnect Socket: {sid}')

    user: UserSessions = user_db.pop(sid)
    for room_id, room in user.rooms.items():
        room.users.pop(user.sid)
        emit('user:disconnected', user.to_dict(), room=room_id)
        if room.closed:
            emit('room:closed', room.to_dict(), namespace=namespace, broadcast=True)


@socket.on('room:join', namespace=namespace)
def blackboard_join(room_id: str):
    sid = request.sid
    room: Optional[BlackboardRoom] = room_db.get(room_id)
    if room is None:
        return

    was_closed = room.closed

    user: UserSessions = user_db.get(sid)
    user.rooms[room_id] = room
    room.users[sid] = user

    join_room(room_id)

    if was_closed:
        msg_data = RoomCreatedData(
            room=room.to_data(),
            room_url=url_for('blackboard.link_to', room_id=room_id))

        socket.emit('room:created', msg_data.to_dict(),
                    namespace=namespace,
                    broadcast=True)

    join_data = RoomJoinedData(user=user.to_data(), room=room.to_data())
    join_data_dict = join_data.to_dict()

    emit('room:user:joined', join_data_dict, room=room_id)
    emit('room:joined', join_data_dict)

    if room.last_data:
        emit('room:print', room.last_data.to_dict(), )


@socket.on('room:update:content', namespace=namespace)
@convert(RoomUpdateContentData)
def blackboard_change_markdown(msg: RoomUpdateContentData):
    sid = request.sid
    user: UserSessions = user_db.get(sid)

    room: BlackboardRoom = room_db.get(msg.room_id)
    if not room:
        return

    data = RoomPrintData(
        text=msg.text,
        markdown=escape(msg.text),
        creator=user.to_data(),
    )

    room.last_data = data

    emit('room:print', data.to_dict(), room=msg.room_id)


@socket.on('user:data:change', namespace=namespace)
@convert(UserDataChangeData)
def blackboard_change_user_data(data: UserDataChangeData):
    sid = request.sid
    user: UserSessions = user_db.get(sid)

    change_counter = 0
    if data.username:
        user.username = data.username
        change_counter += 1

    for room_id, room in user.rooms.items():
        emit('user:data:changed', user.to_dict(), room=room_id)
