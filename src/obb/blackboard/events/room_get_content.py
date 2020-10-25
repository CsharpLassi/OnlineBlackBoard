from dataclasses import dataclass

from flask import escape
from flask_socketio import emit

from obb.ext import socket
from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import UserData
from ..models import BlackboardRoom


@dataclass
class RoomGetContentRequest(BaseRequestMessage):
    page_id: int


@dataclass
class RoomGetContentResponse(BaseResponseMessage):
    page_id: int
    raw_text: str
    markdown: str
    creator: UserData = None


@socket.on('room:get:content', namespace=namespace)
@convert(RoomGetContentRequest)
@event_login_required
def room_get_content(msg: RoomGetContentRequest,
                     room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg.page_id)

    if page_session:
        markdown = page_session.get_markdown()
        data = RoomGetContentResponse(
            page_id=msg.page_id,
            raw_text=markdown,
            markdown=escape(markdown),
        )

        emit('room:get:content', data.to_dict())
