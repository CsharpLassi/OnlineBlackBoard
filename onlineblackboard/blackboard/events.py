from flask_socketio import emit

from ..ext import socket

namespace = 'blackboard'


@socket.on('connect', namespace=namespace)
def on_connect():
    pass
