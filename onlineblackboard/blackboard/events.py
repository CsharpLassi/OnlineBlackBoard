from typing import Optional

from flask import request
from flask_socketio import emit, join_room

from ..ext import socket

from .server_models import UserSessions, BlackboardRoom
from .ext import namespace, room_db, user_db, check_rooms


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    sid = request.sid
    user: UserSessions = user_db.get(sid)
    if user is None:
        user = UserSessions(sid)
        user_db.add(sid, user)
    user.connect()


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    sid = request.sid
    user: UserSessions = user_db.pop(sid)
    user.disconnect()

    check_rooms()
    return


@socket.on('join', namespace=namespace)
def blackboard_join(room_id):
    sid = request.sid
    room: Optional[BlackboardRoom] = room_db.get(room_id)
    if room is None:
        return

    user = user_db.get(sid)
    user.rooms[room_id] = room
    room.users[sid] = user

    join_room(room_id)
    return


@socket.on('change_markdown', namespace=namespace)
def blackboard_change_markdown(msg):
    emit('print_content', {'markdown': msg['text']}, room=msg['room_id'])
    return
