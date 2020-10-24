from dataclasses import dataclass

from flask_login import current_user
from flask_socketio import emit

from .functions import get_page_session
from ..decorators import convert, event_login_required
from ..ext import namespace, bb_session_manager
from ..messages.base_messages import BaseRequestMessage, BaseResponseMessage
from ..models import BlackboardRoom, LecturePage
from ...ext import socket, db


@dataclass
class RoomGetPageRequest(BaseRequestMessage):
    page: int


@dataclass
class RoomGetPageResponse(BaseResponseMessage):
    page_id: int
    width: int
    height: int


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
            height=page.draw_height
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
        if left_page is None and session.session_user_data.allow_new_page:
            left_page = LecturePage()
            left_page.draw_height = room.draw_height
            left_page.draw_width = room.draw_width
            left_page.lecture = page.lecture
            left_page.creator = current_user

            page.left_page = left_page
            left_page.right_page = page

            db.session.commit()

        session.page_id = left_page.id

        data = RoomGetPageResponse(
            page_id=left_page.id,
            width=left_page.draw_width,
            height=left_page.draw_height
        )

        emit('room:get:page', data.to_dict())


@socket.on('room:get:page:right', namespace=namespace)
@convert(RoomGetPageRequest)
@event_login_required
def room_get_page_right(msg: RoomGetPageRequest,
                        room: BlackboardRoom = None):
    session = bb_session_manager.get(msg.session.session_id)

    page_session = get_page_session(session, room, msg_page=msg.page)

    if page_session and (page := LecturePage.get(page_session.page_id)):
        right_page = page.right_page
        if right_page is None and session.session_user_data.allow_new_page:
            right_page = LecturePage()
            right_page.draw_height = room.draw_height
            right_page.draw_width = room.draw_width
            right_page.lecture = page.lecture
            right_page.creator = current_user

            page.right_page = right_page
            right_page.left_page = page

            db.session.commit()

        session.page_id = right_page.id

        data = RoomGetPageResponse(
            page_id=right_page.id,
            width=right_page.draw_width,
            height=right_page.draw_height
        )

        emit('room:get:page', data.to_dict())
