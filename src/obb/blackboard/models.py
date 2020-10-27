from __future__ import annotations

import datetime
from dataclasses import dataclass
from operator import or_
from typing import Optional, Iterator

from dataclasses_json import dataclass_json, LetterCase
from flask_login import current_user
from sqlalchemy.sql import func

from .wrapper import BlackboardRoomWrapper

from ..ext import db

default_draw_height = 256
default_draw_width = 1024
default_visibility = "creator_only"

blackboardRoom_visibilities = ("creator_only", "public")


def create_default_id() -> str:
    from obb.tools import id_generator

    # Todo: test exist
    return id_generator(12)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BlackBoardRoomData:
    id: str
    name: str
    full_name: str

    draw_height: int
    draw_width: int


class BlackboardRoom(db.Model, BlackboardRoomWrapper):
    id = db.Column(db.String, primary_key=True, default=create_default_id)
    name = db.Column(db.String, nullable=False, index=True)

    full_name = db.Column(db.String, nullable=False, index=True, unique=True)

    draw_height = db.Column(
        db.Integer,
        nullable=False,
        default=default_draw_height,
        server_default=str(default_draw_height),
    )

    draw_width = db.Column(
        db.Integer,
        nullable=False,
        default=default_draw_width,
        server_default=str(default_draw_width),
    )

    visibility = db.Column(
        db.String,
        nullable=False,
        server_default=default_visibility,
        default=default_visibility,
    )

    is_invisible = db.Column(
        db.Boolean, nullable=False, server_default="0", default=False
    )

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User")

    lecture_sessions = db.relationship("LectureSession", lazy=True)

    def get_data(self) -> BlackBoardRoomData:
        return BlackBoardRoomData(
            id=self.id,
            name=self.name,
            full_name=self.full_name,
            draw_height=self.draw_height,
            draw_width=self.draw_width,
        )

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

        query = query.filter(
            or_(BlackboardRoom.full_name == name, BlackboardRoom.name == name)
        )

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
            f_query = f_query.filter(
                or_(
                    BlackboardRoom.creator_id == user_id,
                    BlackboardRoom.visibility == "public",
                )
            )

        return f_query.all()


class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False, index=True, unique=True)

    edit_room_id = db.Column(db.Integer, db.ForeignKey("blackboard_room.id"))
    edit_room = db.relationship("BlackboardRoom", foreign_keys=[edit_room_id])

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User")

    start_page_id = db.Column(
        db.Integer, db.ForeignKey("lecture_page.id"), nullable=False
    )
    start_page = db.relationship(
        "LecturePage", post_update=True, foreign_keys=[start_page_id]
    )

    current_page_id = db.Column(
        db.Integer, db.ForeignKey("lecture_page.id"), nullable=False
    )
    current_page = db.relationship(
        "LecturePage", post_update=True, foreign_keys=[current_page_id]
    )

    pages = db.relationship(
        "LecturePage", primaryjoin="Lecture.id == LecturePage.lecture_id"
    )

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

        query = query.filter(
            or_(BlackboardRoom.full_name == name, BlackboardRoom.name == name)
        )

        if query.count() != 1:
            return None

        return query.first()

    @staticmethod
    def get(lecture_id) -> Optional[Lecture]:
        return Lecture.query.get(lecture_id)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LecturePageData:
    id: int
    draw_height: int
    draw_width: int
    lecture_id: int

    left_page_id: int
    right_page_id: int
    top_page_id: int
    bottom_page_id: int


class LecturePage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  # Todo Change to string

    draw_height = db.Column(db.Integer, default=default_draw_height)
    draw_width = db.Column(db.Integer, default=default_draw_width)

    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    lecture = db.relationship("Lecture", uselist=False, foreign_keys=[lecture_id])

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User", uselist=False, foreign_keys=[creator_id])

    left_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))
    left_page = db.relationship(
        "LecturePage", uselist=False, post_update=True, foreign_keys=left_page_id
    )

    right_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))
    right_page = db.relationship(
        "LecturePage", uselist=False, post_update=True, foreign_keys=right_page_id
    )

    top_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))
    top_page = db.relationship(
        "LecturePage", uselist=False, post_update=True, foreign_keys=top_page_id
    )

    bottom_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))
    bottom_page = db.relationship(
        "LecturePage", uselist=False, post_update=True, foreign_keys=bottom_page_id
    )

    def get_data(self) -> LecturePageData:
        return LecturePageData(
            id=self.id,
            draw_height=self.draw_height,
            draw_width=self.draw_width,
            lecture_id=self.lecture_id,
            left_page_id=self.left_page_id,
            right_page_id=self.right_page_id,
            top_page_id=self.top_page_id,
            bottom_page_id=self.bottom_page_id,
        )

    @staticmethod
    def create(lecture: Lecture, creator=None) -> LecturePage:
        if current_user and current_user.is_authenticated:
            creator = current_user

        new_page = LecturePage()
        new_page.lecture = lecture
        new_page.creator = creator

        return new_page

    @staticmethod
    def get(id) -> Optional[LecturePage]:
        if id is None:
            return None
        return LecturePage.query.get(id)


class LectureSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, nullable=False)

    maintainer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    maintainer = db.relationship("User")

    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    lecture = db.relationship("Lecture")

    room_id = db.Column(db.String, db.ForeignKey("blackboard_room.id"), nullable=False)
    room = db.relationship("BlackboardRoom", cascade="all, delete")

    start_time = db.Column(
        db.TIMESTAMP,
        nullable=False,
        default=datetime.datetime.utcnow,
        server_default=func.utcnow(),
    )

    duration = db.Column(db.Integer, nullable=False, default=120, server_default="120")

    end_time: datetime.datetime = property(
        lambda self: self.start_time + datetime.timedelta(minutes=self.duration)
    )

    def is_open(self) -> bool:
        current_time = datetime.datetime.utcnow()
        result = current_time > self.start_time and current_time < self.end_time
        return result

    @staticmethod
    def get_lectures(maintainer_id: int = None) -> Iterator[LectureSession]:
        query = LectureSession.query

        if maintainer_id:
            query = query.filter_by(maintainer_id=maintainer_id)

        return query.all()
