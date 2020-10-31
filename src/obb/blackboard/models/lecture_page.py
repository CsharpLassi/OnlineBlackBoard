from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json, LetterCase

from obb.ext import db
from obb.tools.models.BaseModel import BaseModel
from .defaults import default_draw_height, default_draw_width
from .wrappers.lecture_page import LecturePageWrapper


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LecturePageData:
    id: int
    draw_height: int
    draw_width: int
    lecture_id: int
    is_current_page: bool

    prev_page_id: int = None
    next_pages: List[int] = field(default_factory=list)


class LecturePage(db.Model, BaseModel, LecturePageWrapper):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)  # Todo Change to string

    draw_height = db.Column(db.Integer, default=default_draw_height)
    draw_width = db.Column(db.Integer, default=default_draw_width)

    lecture_id = db.Column(db.Integer, db.ForeignKey("lecture.id"), nullable=False)
    lecture = db.relationship("Lecture", foreign_keys=[lecture_id], backref="pages")

    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User")

    prev_page_id = db.Column(db.Integer, db.ForeignKey("lecture_page.id"))
    prev_page = db.relationship("LecturePage", remote_side=[id])

    def get_data(self) -> LecturePageData:
        return LecturePageData(
            id=self.id,
            draw_height=self.draw_height,
            draw_width=self.draw_width,
            lecture_id=self.lecture_id,
            is_current_page=self.lecture.current_page == self,
            prev_page_id=self.prev_page_id,
            next_pages=[page.id for page in self.next_pages],
        )
