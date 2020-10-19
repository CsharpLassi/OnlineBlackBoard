from flask import request, current_app, escape
from flask_socketio import emit, join_room

from .components.session_manager import BlackBoardSession

from .messages.request_messages import *
from .messages.response_messages import *

from .decorators import convert, to_form_dict, event_login_required
from .ext import namespace, bb_session_manager

from .models import BlackboardRoom
from .msg import *

from ..ext import socket, db


@socket.on('connect', namespace=namespace)
def blackboard_connect():
    sid = request.sid
    current_app.logger.debug(f'Connect Socket: {sid}')


@socket.on('disconnect', namespace=namespace)
def blackboard_disconnect():
    sid = request.sid
    current_app.logger.debug(f'Disconnect Socket: {sid}')

    session = bb_session_manager.leave(sid)
    if session:
        leave_data = UserLeaveResponse(
            user=session.session_user_data,
            room=session.session_room_data
        )

        emit('room:user:leave', leave_data.to_dict(), room=session.room_id)


@socket.on('room:join', namespace=namespace)
@convert(JoinRequestMessage)
@event_login_required
def blackboard_join(msg: JoinRequestMessage, room: BlackboardRoom = None):
    sid = request.sid
    session: BlackBoardSession = bb_session_manager.get(msg.session.session_id)

    join_room(room.id)
    bb_session_manager.join(sid, msg.session.session_id)

    response_data = UserJoinedResponse(
        user=session.session_user_data,
        room=session.session_room_data)
    response_data_dict = response_data.to_dict()

    emit('room:user:joined', response_data_dict, room=room.id)
    emit('room:joined', response_data_dict)


@socket.on('room:update:content', namespace=namespace)
@convert(RoomUpdateContentRequestMessage)
@event_login_required
def blackboard_room_update_content(msg: RoomUpdateContentRequestMessage,
                                   room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)
    data = RoomPrintResponse(
        raw_text=msg.raw_text,
        markdown=escape(msg.raw_text),
        creator=session.session_user_data,
    )

    emit('room:print', data.to_dict(), room=room.id)


@socket.on('room:update:draw', namespace=namespace)
@convert(RoomDrawRequestMessage)
@event_login_required
def room_update_draw(msg: RoomDrawRequestMessage, room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    data = RoomDrawResponseMessage(
        stroke=msg.stroke,
        creator=session.session_user_data,
    )

    emit('room:draw:stroke', data.to_dict(), room=room.id)


@socket.on('room:update:settings', namespace=namespace)
@to_form_dict(item='from_data')
@convert(RoomUpdateSettingsRequestMessage)
@event_login_required
def blackboard_room_update_settings(msg: RoomUpdateSettingsRequestMessage, form_data,
                                    room: BlackboardRoom = None):
    from .forms import RoomSettings
    room_settings = RoomSettings(form_data)
    if room_settings.validate():
        room.draw_height = room_settings.height.data
        room.visibility = room_settings.visibility.data

        db.session.commit()

        data = RoomUpdateSettingsResponseMessage(
            content_draw_height=room.draw_height
        )

        emit('room:updated:settings', data.to_dict(), room=room.id)
