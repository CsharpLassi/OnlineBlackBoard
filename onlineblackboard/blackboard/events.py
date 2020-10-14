from flask_socketio import emit

from ..ext import socket

namespace = '/blackboard'


@socket.on('connect', namespace='/blackboard')
def blackboard_connect():
    emit('print_content', {'markdown': '# Connected'})
