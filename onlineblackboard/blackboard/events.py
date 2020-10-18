from typing import Optional

from flask import request, current_app, escape, url_for
from flask_login import current_user
from flask_socketio import emit, join_room

from .ext import namespace, room_db, user_db
from .server_models import UserSessions, BlackboardRoom
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
def blackboard_join(room_id, msg: dict = None):
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
            room_id=room_id,
            room_url=url_for('blackboard.link_to', room_id=room_id))

        socket.emit('room:created', msg_data.to_dict(),
                    namespace=namespace,
                    broadcast=True)

    emit('room:user:joined', user.to_dict(), room=room_id)
    emit('room:joined', user.to_dict())


@socket.on('room:update:content', namespace=namespace)
def blackboard_change_markdown(msg):
    sid = request.sid
    user: UserSessions = user_db.get(sid)

    text = escape(msg['text'])

    data = {
        'raw_markdown': msg['text'],
        'markdown': text,
        'creator': user.to_dict()
    }

    emit('room:print', data, room=msg['room_id'])


@socket.on('user:data:change', namespace=namespace)
def blackboard_change_user_data(data: dict):
    sid = request.sid
    user: UserSessions = user_db.get(sid)

    change_counter = 0
    if 'username' in data:
        user.username = data['username']
        change_counter += 1

    emit('user:data:changed', user.to_dict(), broadcast=True)
