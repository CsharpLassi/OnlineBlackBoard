from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage
from ..messages.datas import StrokeData, UserData
from ..models import BlackboardRoom


@dataclass
class RoomGetSketchRequest(BaseRequestMessage):
    page: int = 0


@dataclass
class RoomGetSketchResponse(BaseRequestMessage):
    stroke: StrokeData
    creator: UserData = None


@socket.on('room:get:sketch', namespace=namespace)
@convert(RoomGetSketchRequest)
@event_login_required
def room_get_sketch(msg: RoomGetSketchRequest,
                    room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    # Read Markdown
    l_session = room.get_current_lecture_session()
    lecture = l_session.lecture

    page_id = msg.page or lecture.current_page_id or lecture.start_page_id
    page_session = page_manager.get(page_id, lecture=lecture)

    if page_session:
        for stroke in page_session.get_strokes():
            data = RoomGetSketchResponse(
                stroke=stroke,
            )

            emit('room:draw:stroke', data.to_dict())
