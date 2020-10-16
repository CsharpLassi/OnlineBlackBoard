from flask_socketio import emit, join_room

from ..ext import socket

from .ext import namespace, id_generator


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    return


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    return


@socket.on('get_room', namespace=namespace)
def blackboard_get_room():
    room_id = id_generator()
    join_room(room_id)
    emit('change_room', {'room_id': room_id})


@socket.on('join', namespace=namespace)
def blackboard_join(room_id):
    join_room(room_id)
    return


@socket.on('change_markdown', namespace=namespace)
def blackboard_change_markdown(msg):
    emit('print_content', {'markdown': msg['text']}, room=msg['room_id'])
    return
