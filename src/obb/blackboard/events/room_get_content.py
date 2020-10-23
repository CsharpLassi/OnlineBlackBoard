from dataclasses import dataclass
from flask import escape
from flask_socketio import emit

from obb.ext import socket
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import UserData
from ..models import BlackboardRoom


@dataclass
class RoomGetContentRequest(BaseRequestMessage):
    page: int = 0


@dataclass
class RoomGetContentResponse(BaseResponseMessage):
    raw_text: str
    markdown: str
    creator: UserData = None


@socket.on('room:get:content', namespace=namespace)
@convert(RoomGetContentRequest)
@event_login_required
def room_get_content(msg: RoomGetContentRequest,
                                room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    # Read Markdown
    l_session = room.get_current_lecture_session()
    lecture = l_session.lecture

    page_id = msg.page or lecture.current_page_id or lecture.start_page_id
    page_session = page_manager.get(page_id, lecture=lecture)

    if page_session and (markdown := page_session.get_markdown()):
        data = RoomGetContentResponse(
            raw_text=markdown,
            markdown=escape(markdown),
        )

        emit('room:print', data.to_dict())
