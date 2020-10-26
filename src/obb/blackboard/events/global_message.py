from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase

from obb.blackboard.memory import MemoryLecturePageData, MemoryUserData
from obb.blackboard.messages.base_messages import BaseResponseMessage


@dataclass
class RoomUpdatedMessage(BaseResponseMessage):
    page_id: int
    width: int
    height: int

    has_left_page: bool
    has_right_page: bool


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NewLecturePageEvent:
    page: MemoryLecturePageData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserUpdatedEvent:
    user: MemoryUserData
    all: bool
    changes: list = field(default_factory=list)
