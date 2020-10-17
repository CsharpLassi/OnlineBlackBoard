from typing import Optional

from flask import request, current_app
from flask_login import current_user
from flask_socketio import emit, join_room

from .ext import namespace, room_db, user_db
from .server_models import UserSessions, BlackboardRoom
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

    emit('user_left', user.get_msg_data(), broadcast=True)

    return


@socket.on('join', namespace=namespace)
def blackboard_join(room_id, msg: dict = None):
    sid = request.sid
    room: Optional[BlackboardRoom] = room_db.get(room_id)
    if room is None:
        return

    user: UserSessions = user_db.get(sid)
    user.rooms[room_id] = room
    room.users[sid] = user

    join_room(room_id)

    emit('user_joined', user.get_msg_data(), room=room_id)
    emit('joined', user.get_msg_data())


@socket.on('change_markdown', namespace=namespace)
def blackboard_change_markdown(msg):
    emit('print_content', {'markdown': msg['text']}, room=msg['room_id'])
    return


@socket.on('change_user_data', namespace=namespace)
def blackboard_change_user_data(data: dict):
    sid = request.sid
    user: UserSessions = user_db.get(sid)

    change_counter = 0
    if 'username' in data:
        user.username = data['username']
        change_counter += 1

    emit('user_changed_data', user.get_msg_data(), broadcast=True)
