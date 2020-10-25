from dataclasses import dataclass

from flask_socketio import emit

from obb.ext import socket
from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager, page_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..messages.datas import StrokeData, UserData
from ..models import BlackboardRoom


@dataclass
class RoomClearSketchRequest(BaseRequestMessage):
    pass


@dataclass
class RoomClearSketchResponse(BaseResponseMessage):
    creator: UserData = None


@socket.on('room:clear:sketch', namespace=namespace)
@convert(RoomClearSketchRequest)
@event_login_required
def room_update_sketch(msg: RoomClearSketchRequest,
                       room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    if not session.session_user_data.allow_draw:
        # Todo: Msg
        return

    data = RoomClearSketchResponse(
        creator=session.session_user_data,
    )

    emit('room:clear:sketch', data.to_dict(), room=room.id)

    # Save History
    page_session = get_page_session(session, room)
    if page_session:
        page_session.clear_stroke()
