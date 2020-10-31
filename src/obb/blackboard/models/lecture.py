from dataclasses import dataclass

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import db
from obb.tools.models.BaseModel import BaseModel
from .wrappers.lecture import LectureWrapper


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LectureData:
    id: int
    name: str


class Lecture(db.Model, BaseModel, LectureWrapper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User")

    constraint_creator_name = db.UniqueConstraint(creator_id, name)

    edit_room_id = db.Column(db.String, db.ForeignKey("blackboard_room.id"))
    edit_room = db.relationship("BlackboardRoom", foreign_keys=[edit_room_id])

    current_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))

    def get_data(self) -> LectureData:
        return LectureData(id=self.id, name=self.name)
