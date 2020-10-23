from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket, db
from ..decorators import to_form_dict, convert, event_login_required
from ..ext import namespace
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..models import BlackboardRoom
from ..forms import RoomSettings


@dataclass
class RoomUpdateSettingsRequest(BaseRequestMessage):
    pass


@dataclass()
class RoomUpdateSettingsResponse(BaseResponseMessage):
    content_draw_height: int


@socket.on('room:update:settings', namespace=namespace)
@to_form_dict(item='form_data')
@convert(RoomUpdateSettingsRequest)
@event_login_required
def room_update_settings(msg: RoomUpdateSettingsRequest, form_data,
                                    room: BlackboardRoom = None):
    room_settings = RoomSettings(form_data)
    if room_settings.validate():
        room_settings.write_data(room)

        db.session.commit()

        data = RoomUpdateSettingsResponse(
            content_draw_height=room.draw_height
        )

        emit('room:update:settings', data.to_dict(), room=room.id)
