from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import StrokeData, UserData
from ..models import BlackboardRoom


@dataclass
class RoomUpdateSketchRequest(BaseRequestMessage):
    stroke: StrokeData


@dataclass
class RoomUpdateSketchResponse(BaseResponseMessage):
    stroke: StrokeData
    creator: UserData = None


@socket.on('room:update:sketch', namespace=namespace)
@convert(RoomUpdateSketchRequest)
@event_login_required
def room_update_sketch(msg: RoomUpdateSketchRequest,
                       room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    if not session.session_user_data.allow_draw:
        # Todo: Msg
        return

    data = RoomUpdateSketchResponse(
        stroke=msg.stroke,
        creator=session.session_user_data,
    )

    emit('room:draw:stroke', data.to_dict(), room=room.id)

    # Save History
    l_session = room.get_current_lecture_session()
    lecture = l_session.lecture

    page_id = lecture.current_page_id or lecture.start_page_id
    page_session = page_manager.get(page_id, lecture=lecture)

    page_session.add_stroke(data.stroke)
