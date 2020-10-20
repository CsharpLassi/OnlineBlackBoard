from __future__ import annotations

from operator import or_
from typing import Optional, Iterator

import datetime

from sqlalchemy.sql import func

from ..ext import db

default_draw_height = 256
default_draw_width = 1024
default_visibility = 'creator_only'

blackboardRoom_visibilities = ('creator_only', 'public')


def create_default_id() -> str:
    from obb.tools import id_generator
    return id_generator(12)


class BlackboardRoom(db.Model):
    id = db.Column(db.String, primary_key=True, default=create_default_id)
    name = db.Column(db.String,
                     nullable=False,
                     index=True)
    full_name = db.Column(db.String,
                          nullable=False,
                          index=True,
                          unique=True)

    draw_height = db.Column(db.Integer,
                            nullable=False,
                            default=default_draw_height,
                            server_default=str(default_draw_height))

    draw_width = db.Column(db.Integer,
                           nullable=False,
                           default=default_draw_width,
                           server_default=str(default_draw_width))

    visibility = db.Column(db.String, nullable=False,
                           server_default=default_visibility,
                           default=default_visibility)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    lecture_sessions = db.relationship('LectureSession', lazy=True)

    def can_join(self, user=None) -> bool:
        from flask_login import current_user
        from ..users.models import User

        is_open = False
        for session in self.lecture_sessions:
            if session.is_open():
                is_open = True
                break

        if not is_open:
            return False

        if isinstance(user, int):
            user = User.get(user)

        if not user and current_user.is_authenticated:
            user = current_user

        user_id = 0 if not user else user.id

        if user_id == self.creator_id:
            return True

        if self.visibility == 'public':
            return True

        return False

    def get_style(self) -> str:
        style = ''
        if self.draw_height > 0:
            style += f'height:{self.draw_height}px;'
        if self.draw_width > 0:
            style += f'width:{self.draw_width}px;'
        return style

    @staticmethod
    def get(id) -> Optional[BlackboardRoom]:
        return BlackboardRoom.query.get(id)

    @staticmethod
    def get_by_name(name: str) -> Optional[BlackboardRoom]:
        query_name = BlackboardRoom.query.filter_by(name=name)
        if query_name.count() == 1:
            return query_name.first()

        query_fullname = BlackboardRoom.query.filter_by(full_name=name)
        return query_fullname.first()

    @staticmethod
    def get_rooms(user=None, public=False) -> Iterator[BlackboardRoom]:
        from flask_login import current_user
        from ..users.models import User

        if isinstance(user, int):
            user = User.get(user)

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        user_id = 0 if not user else user.id

        f_query = BlackboardRoom.query

        if not public:
            f_query = f_query.filter(BlackboardRoom.creator_id == user_id)
        else:
            f_query = f_query.filter(or_(BlackboardRoom.creator_id == user_id,
                                         BlackboardRoom.visibility == 'public'))

        return f_query.all()


class LectureSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    maintainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    maintainer = db.relationship('User')

    room_id = db.Column(db.String, db.ForeignKey('blackboard_room.id'), nullable=False)
    room = db.relationship('BlackboardRoom')

    start_time = db.Column(db.DATETIME, nullable=False,
                           default=datetime.datetime.utcnow,
                           server_default=func.utcnow())

    duration = db.Column(db.Integer, nullable=False, default=120, server_default='120')

    end_time: datetime.datetime = property(
        lambda self: self.start_time + datetime.timedelta(self.duration))

    def is_open(self) -> bool:
        current_time = datetime.datetime.utcnow()

        return current_time > self.start_time and current_time < self.end_time
