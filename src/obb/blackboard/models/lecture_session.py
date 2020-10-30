import datetime

from obb.ext import db
from obb.tools.models.BaseModel import BaseModel
from .defaults import default_lecture_session_visibility
from .wrappers.lecture_session import LectureSessionWrapper


class LectureSession(db.Model, BaseModel, LectureSessionWrapper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    maintainer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    maintainer = db.relationship("User")

    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    lecture = db.relationship("Lecture")

    room_id = db.Column(db.String, db.ForeignKey("blackboard_room.id"), nullable=False)
    room = db.relationship("BlackboardRoom", cascade="all, delete")

    visibility = db.Column(
        db.String,
        nullable=False,
        server_default=default_lecture_session_visibility,
        default=default_lecture_session_visibility,
    )

    start_time = db.Column(
        db.TIMESTAMP, nullable=False, default=datetime.datetime.utcnow
    )

    duration = db.Column(db.Integer, nullable=False, default=120, server_default="120")

    end_time: datetime.datetime = property(
        lambda self: self.start_time + datetime.timedelta(minutes=self.duration)
    )

    def is_open(self) -> bool:
        current_time = datetime.datetime.utcnow()
        result = current_time > self.start_time and current_time < self.end_time
        return result
