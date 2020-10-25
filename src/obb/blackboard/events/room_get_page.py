from dataclasses import dataclass

from flask_login import current_user
from flask_socketio import emit

from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..models import BlackboardRoom, LecturePage
from ...ext import socket, db

from .global_message import RoomUpdatedMessage


@dataclass
class RoomGetPageRequest(BaseRequestMessage):
    page: int
    insert: bool = False


@dataclass
class RoomGetPageResponse(RoomUpdatedMessage):
    pass


@socket.on('room:get:page', namespace=namespace)
@convert(RoomGetPageRequest)
@event_login_required
def room_get_page(msg: RoomGetPageRequest,
                  room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg_page=msg.page)

    if page_session and (page := LecturePage.get(page_session.page_id)):
        session.page_id = page.id

        data = RoomGetPageResponse(
            page_id=page_session.page_id,
            width=page.draw_width,
            height=page.draw_height,
            has_left_page=page.left_page is not None,
            has_right_page=page.right_page is not None,
        )

        emit('room:get:page', data.to_dict())


@socket.on('room:get:page:left', namespace=namespace)
@convert(RoomGetPageRequest)
@event_login_required
def room_get_page_left(msg: RoomGetPageRequest,
                       room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg_page=msg.page)

    if page_session and (page := LecturePage.get(page_session.page_id)):
        left_page = page.left_page
        if left_page is None and msg.insert and session.session_user_data.allow_new_page:
            left_page = LecturePage()
            left_page.draw_height = room.draw_height
            left_page.draw_width = room.draw_width
            left_page.lecture = page.lecture
            left_page.creator = current_user

            page.left_page = left_page
            left_page.right_page = page

            db.session.commit()

        session.page_id = left_page.id

        response_data = RoomGetPageResponse(
            page_id=left_page.id,
            width=left_page.draw_width,
            height=left_page.draw_height,
            has_left_page=left_page.left_page is not None,
            has_right_page=left_page.right_page is not None,
        )

        emit('room:get:page', response_data.to_dict())


@socket.on('room:get:page:right', namespace=namespace)
@convert(RoomGetPageRequest)
@event_login_required
def room_get_page_right(msg: RoomGetPageRequest,
                        room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg_page=msg.page)

    if page_session and (page := LecturePage.get(page_session.page_id)):
        right_page = page.right_page
        if (right_page is None or msg.insert) and \
                session.session_user_data.allow_new_page:
            new_page = LecturePage()
            new_page.draw_height = room.draw_height
            new_page.draw_width = room.draw_width
            new_page.lecture = page.lecture
            if current_user and current_user.is_authenticated:
                new_page.creator = current_user

            page.right_page = new_page
            new_page.left_page = page

            if right_page:
                right_page.left_page = new_page
                new_page.right_page = right_page

            db.session.commit()

            right_page = new_page

        session.page_id = right_page.id

        data = RoomGetPageResponse(
            page_id=right_page.id,
            width=right_page.draw_width,
            height=right_page.draw_height,
            has_left_page=right_page.left_page is not None,
            has_right_page=right_page.right_page is not None,
        )

        emit('room:get:page', data.to_dict())
