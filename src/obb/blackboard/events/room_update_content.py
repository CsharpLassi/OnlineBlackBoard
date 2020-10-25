from dataclasses import dataclass
from flask import escape
from flask_socketio import emit

from obb.ext import socket
from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import UserData
from ..models import BlackboardRoom


@dataclass
class RoomUpdateContentRequest(BaseRequestMessage):
    page_id: int
    raw_text: str


@dataclass
class RoomUpdateContentResponse(BaseResponseMessage):
    page_id: int
    raw_text: str
    markdown: str
    creator: UserData = None


@socket.on('room:update:content', namespace=namespace)
@convert(RoomUpdateContentRequest)
@event_login_required
def room_update_content(msg: RoomUpdateContentRequest,
                        room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)
    data = RoomUpdateContentResponse(
        page_id=msg.page_id,
        raw_text=msg.raw_text,
        markdown=escape(msg.raw_text),
        creator=session.session_user_data,
    )

    emit('room:update:content', data.to_dict(), room=room.id)

    # Save Markdown
    page_session = get_page_session(session, room, msg_page=msg.page_id)

    if page_session:
        page_session.set_markdown(msg.raw_text)
