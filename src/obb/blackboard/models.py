from __future__ import annotations

from operator import or_
from typing import Optional, Iterator

import datetime

from flask_login import current_user
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

    is_invisible = db.Column(db.Boolean, nullable=False,
                             server_default='0',
                             default=False)

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    lecture_sessions = db.relationship('LectureSession', lazy=True)

    def get_style(self) -> str:
        style = ''
        if self.draw_height > 0:
            style += f'height:{self.draw_height}px;'
        if self.draw_width > 0:
            style += f'width:{self.draw_width}px;'
        return style

    def get_current_lecture_session(self) -> Optional[LectureSession]:
        lecture: LectureSession
        for lecture in self.lecture_sessions:
            if lecture.is_open():
                return lecture

        return None

    def intersect_lecture(self, start_time: datetime.datetime, duration: int) -> bool:
        end_time: datetime.datetime = start_time + datetime.timedelta(minutes=duration)
        lecture: LectureSession

        for lecture in self.lecture_sessions:
            if lecture.start_time < start_time < lecture.end_time:
                return True

            if lecture.start_time < end_time < lecture.end_time:
                return True

            if start_time < lecture.start_time < end_time:
                return True

            if start_time < lecture.end_time < end_time:
                return True

        return False

    @staticmethod
    def get(id) -> Optional[BlackboardRoom]:
        return BlackboardRoom.query.get(id)

    @staticmethod
    def get_by_name(name: str, user=None) -> Optional[BlackboardRoom]:
        if not user and current_user and current_user.is_authenticated:
            user = current_user

        if not user:
            return None

        query = BlackboardRoom.query

        query = query.filter_by(creator_id=user.id, is_invisible=False)

        query = query.filter(or_(BlackboardRoom.full_name == name,
                                 BlackboardRoom.name == name))

        if query.count() != 1:
            return None

        return query.first()

    @staticmethod
    def get_rooms(user=None, usable=False) -> Iterator[BlackboardRoom]:
        from flask_login import current_user
        from ..users.models import User

        if isinstance(user, int):
            user = User.get(user)

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        user_id = 0 if not user else user.id

        f_query = BlackboardRoom.query
        f_query = f_query.filter_by(is_invisible=False)

        if not usable:
            f_query = f_query.filter(BlackboardRoom.creator_id == user_id)
        else:
            f_query = f_query.filter(or_(BlackboardRoom.creator_id == user_id,
                                         BlackboardRoom.visibility == 'public'))

        return f_query.all()


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False, index=True, unique=True)

    edit_room_id = db.Column(db.Integer, db.ForeignKey('blackboard_room.id'))
    edit_room = db.relationship('BlackboardRoom', foreign_keys=[edit_room_id])

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User')

    start_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    start_page = db.relationship('LecturePage', foreign_keys=[start_page_id])

    current_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    current_page = db.relationship('LecturePage', foreign_keys=[current_page_id])

    pages = db.relationship('LecturePage',
                            primaryjoin="Lecture.id == LecturePage.lecture_id")

    def get_page(self, page_id: int = None, width: int = None, height: int = None) \
            -> Optional[LecturePage]:
        if page_id is None:
            page_id = self.current_page_id or self.start_page_id

        page = LecturePage.get(page_id)

        if page and page.lecture_id != self.id:
            # Todo: Exception
            return None

        if page is None:
            page = LecturePage()
            page.lecture = self
            page.creator = current_user
            page.draw_width = width
            page.draw_height = height

            self.start_page = self.current_page = page
            db.session.commit()
        return page

    @staticmethod
    def get_lectures(user=None) -> Iterator[Lecture]:
        if not user and current_user and current_user.is_authenticated:
            user = current_user

        query = Lecture.query
        if user:
            query = query.filter_by(creator_id=user.id)

        return query

    @staticmethod
    def get_by_name(name: str, user=None) -> Optional[Lecture]:
        if not user and current_user and current_user.is_authenticated:
            user = current_user

        if not user:
            return None

        query = Lecture.query

        query = query.filter_by(creator_id=user.id)

        query = query.filter(or_(BlackboardRoom.full_name == name,
                                 BlackboardRoom.name == name))

        if query.count() != 1:
            return None

        return query.first()

    @staticmethod
    def get(lecture_id) -> Optional[Lecture]:
        return Lecture.query.get(lecture_id)


class LecturePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)

    draw_height = db.Column(db.Integer, default=default_draw_height)
    draw_width = db.Column(db.Integer, default=default_draw_width)

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)
    lecture = db.relationship('Lecture', uselist=False, foreign_keys=[lecture_id])

    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', uselist=False, foreign_keys=[creator_id])

    left_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    left_page = db.relationship('LecturePage', uselist=False, post_update=True,
                                foreign_keys=[left_page_id])

    right_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    right_page = db.relationship('LecturePage', uselist=False, post_update=True,
                                 foreign_keys=[right_page_id])

    top_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    top_page = db.relationship('LecturePage', uselist=False, post_update=True,
                               foreign_keys=[top_page_id])

    bottom_page_id = db.Column(db.Integer, db.ForeignKey('lecture_page.id'))
    bottom_page = db.relationship('LecturePage', uselist=False, post_update=True,
                                  foreign_keys=[bottom_page_id])

    @staticmethod
    def get(page_id: int) -> Optional[LecturePage]:
        if page_id is None:
            return None
        return LecturePage.query.get(page_id)


class LectureSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)

    maintainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    maintainer = db.relationship('User')

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)
    lecture = db.relationship('Lecture')

    room_id = db.Column(db.String, db.ForeignKey('blackboard_room.id'), nullable=False)
    room = db.relationship('BlackboardRoom', cascade="all, delete")

    start_time = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.datetime.utcnow,
                           server_default=func.utcnow())

    duration = db.Column(db.Integer, nullable=False, default=120, server_default='120')

    end_time: datetime.datetime = property(
        lambda self: self.start_time + datetime.timedelta(minutes=self.duration))

    def is_open(self) -> bool:
        current_time = datetime.datetime.utcnow()
        result = current_time > self.start_time and current_time < self.end_time
        return result

    @staticmethod
    def get_lectures(maintainer_id: int = None) \
            -> Iterator[LectureSession]:
        query = LectureSession.query

        if maintainer_id:
            query = query.filter_by(maintainer_id=maintainer_id)

        return query.all()
