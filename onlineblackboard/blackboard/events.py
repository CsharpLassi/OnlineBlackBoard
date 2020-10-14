import string
import random

from flask_socketio import emit, join_room, rooms

from ..ext import socket

from .config import namespace


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    return


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    return


@socket.on('get_room', namespace=namespace)
def blackboard_get_room():
    room_id = id_generator()
    join_room(room_id, namespace=namespace)
    emit('change_room', {'room_id': room_id})


@socket.on('join', namespace=namespace)
def blackboard_get_room(room_id):
    join_room(room_id, namespace=namespace)
    emit('print_content', {'markdown': '# Connected'}, broadcast=True)
    return


@socket.on('change_markdown', namespace=namespace)
def blackboard_get_room(msg):
    emit('print_content', {'markdown': msg['text']}, broadcast=True)
    return
