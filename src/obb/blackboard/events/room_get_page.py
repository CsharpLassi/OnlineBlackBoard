from dataclasses import dataclass

from flask_socketio import emit

from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..models import BlackboardRoom, LecturePage
from ...ext import socket


@dataclass
class RoomGetPageRequest(BaseRequestMessage):
    pass


@dataclass
class RoomGetPageResponse(BaseResponseMessage):
    page_id: int
    width: int
    height: int


@socket.on('room:get:page', namespace=namespace)
@convert(RoomGetPageRequest)
@event_login_required
def room_get_content(msg: RoomGetPageRequest,
                     room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room)

    if page_session and (page := LecturePage.get(page_session.page_id)):
        data = RoomGetPageResponse(
            page_id=page_session.page_id,
            width=page.draw_width,
            height=page.draw_height
        )

        emit('room:get:page', data.to_dict())
