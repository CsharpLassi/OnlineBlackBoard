from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket, db
from .functions import get_page_session
from ..decorators import to_form_dict, convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..models import BlackboardRoom, LecturePage
from ..forms import RoomSettings


@dataclass
class RoomUpdateSettingsRequest(BaseRequestMessage):
    pass


@dataclass()
class RoomUpdateSettingsResponse(BaseResponseMessage):
    content_draw_height: int
    content_draw_width: int


@socket.on('room:update:settings', namespace=namespace)
@to_form_dict(item='form_data')
@convert(RoomUpdateSettingsRequest)
@event_login_required
def room_update_settings(msg: RoomUpdateSettingsRequest, form_data,
                         room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    room_settings = RoomSettings(form_data)
    if room_settings.validate():
        room_settings.write_data(room)

        page_session = get_page_session(session, room)
        if page_session:
            page = LecturePage.get(page_session.page_id)
            page.draw_height = room.draw_height
            page.draw_width = room.draw_width

        db.session.commit()

        data = RoomUpdateSettingsResponse(
            content_draw_height=room.draw_height,
            content_draw_width=room.draw_width
        )

        emit('room:update:settings', data.to_dict(), room=room.id)
