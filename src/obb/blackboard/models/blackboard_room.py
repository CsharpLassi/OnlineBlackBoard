from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from obb.ext import db
from obb.tools.models.BaseModel import BaseModel
from .defaults import (
    default_blackboard_visibility,
    default_draw_height,
    default_draw_width,
)
from .wrappers.blackboard_room import BlackboardRoomWrapper


def create_default_id() -> str:
    from obb.tools import id_generator

    return id_generator(12)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BlackBoardRoomData:
    id: str
    name: str

    draw_height: int
    draw_width: int


class BlackboardRoom(db.Model, BaseModel, BlackboardRoomWrapper):
    id = db.Column(db.String, primary_key=True, default=create_default_id)
    name = db.Column(db.String, nullable=False, index=True)

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    creator = db.relationship("User")

    constraint_creator_name = db.UniqueConstraint(creator_id, name)

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
        server_default=default_blackboard_visibility,
        default=default_blackboard_visibility,
    )

    is_invisible = db.Column(
        db.Boolean, nullable=False, server_default="0", default=False
    )

    sessions = db.relationship("LectureSession", lazy=True)

    def get_data(self) -> BlackBoardRoomData:
        return BlackBoardRoomData(
            id=self.id,
            name=self.name,
            draw_height=self.draw_height,
            draw_width=self.draw_width,
        )
