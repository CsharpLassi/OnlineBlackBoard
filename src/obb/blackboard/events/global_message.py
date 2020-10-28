from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase

from obb.blackboard.memory import MemoryLecturePageData, MemorySessionUserData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NewLecturePageEvent:
    page: MemoryLecturePageData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserUpdatedEvent:
    user: MemorySessionUserData
    all: bool
    changes: list = field(default_factory=list)


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PageUpdatedEvent:
    page: MemoryLecturePageData
    all: bool
    changes: list = field(default_factory=list)
