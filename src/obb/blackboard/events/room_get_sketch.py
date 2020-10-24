from dataclasses import dataclass, field
from typing import List, Optional

from flask_socketio import emit

from obb.ext import socket
from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import StrokeData, UserData
from ..models import BlackboardRoom, Lecture


@dataclass
class RoomGetSketchRequest(BaseRequestMessage):
    page: int = 0


@dataclass
class RoomGetSketchResponse(BaseResponseMessage):
    strokes: List[StrokeData] = field(default_factory=list)


@socket.on('room:get:sketch', namespace=namespace)
@convert(RoomGetSketchRequest)
@event_login_required
def room_get_sketch(msg: RoomGetSketchRequest,
                    room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg.page)

    if page_session:
        data = RoomGetSketchResponse(
            strokes=list(page_session.get_strokes()),
        )

        emit('room:get:sketch', data.to_dict())
