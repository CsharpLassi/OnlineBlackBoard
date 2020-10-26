from .base_messages import Response
from flask_socketio import emit


def emit_error(msg: str):
    response = Response(success=False)
    response.errors.append(msg)
    emit('service:error', response.to_dict())


def emit_success(service: str, item, **kwargs):
    response = Response(success=True)
    response.item = item

    if isinstance(item, list):
        response.count = len(item)

    emit(service, response.to_dict(), **kwargs)
