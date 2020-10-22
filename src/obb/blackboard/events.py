from flask import request, current_app, escape
from flask_login import current_user
from flask_socketio import emit, join_room

from obb.users.models import User

from .components.session_manager import BlackBoardSession

from .messages.request_messages import *
from .messages.response_messages import *

from .decorators import convert, to_form_dict, event_login_required
from .ext import namespace, bb_session_manager

from .models import BlackboardRoom, LecturePage

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

    user: User = session.get_user()
    if not user and room.can_join(session, user=user):
        return

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

    l_session = room.get_current_lecture_session()
    lecture = l_session.lecture

    current_page = lecture.current_page
    # Todo: Verallgemeinern
    if current_page is None:
        page = LecturePage()
        page.lecture = lecture
        page.creator = current_user

        lecture.start_page = lecture.current_page = page
        db.session.commit()

    emit('room:print', data.to_dict(), room=room.id)


@socket.on('room:update:draw', namespace=namespace)
@convert(RoomDrawRequestMessage)
@event_login_required
def room_update_draw(msg: RoomDrawRequestMessage, room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    if not session.session_user_data.allow_draw:
        # Todo: Msg
        return

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
        room_settings.write_data(room)

        db.session.commit()

        data = RoomUpdateSettingsResponseMessage(
            content_draw_height=room.draw_height
        )

        emit('room:updated:settings', data.to_dict(), room=room.id)


@socket.on('room:update:user', namespace=namespace)
@convert(RoomUpdateUserRequestMessage)
@event_login_required
def blackboard_room_update_user(msg: RoomUpdateUserRequestMessage,
                                room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)
    updated_user = bb_session_manager.get_user(msg.user_id)

    update_counter = 0

    allow_change = session.session_user_data.creator
    if allow_change:
        if updated_user and msg.allow_draw is not None:
            updated_user.allow_draw = msg.allow_draw
            update_counter += 1

    response_data = RoomUpdateUserResponseMessage(
        user=updated_user,
    )
    if update_counter > 0:
        emit('room:updated:user', response_data.to_dict(), room=room.id)
    else:
        emit('room:updated:user', response_data.to_dict())
