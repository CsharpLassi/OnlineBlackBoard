from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket
from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import StrokeData, UserData
from ..models import BlackboardRoom


@dataclass
class RoomUpdateSketchRequest(BaseRequestMessage):
    page_id: int
    stroke: StrokeData


@dataclass
class RoomUpdateSketchResponse(BaseResponseMessage):
    page_id: int
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

    if len(msg.stroke.points) < 2:
        return

    data = RoomUpdateSketchResponse(
        page_id=msg.page_id,
        stroke=msg.stroke,
        creator=session.session_user_data,
    )

    emit('room:update:sketch', data.to_dict(), room=room.id)

    # Save History
    page_session = get_page_session(session, room, msg_page=msg.page_id)
    if page_session:
        page_session.add_stroke(data.stroke)
