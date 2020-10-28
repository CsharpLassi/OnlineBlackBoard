__all__ = [
    "room_memory",
    "MemoryBlackboardRoom",
    "MemoryBlackboardRoomData",
    "user_session_memory",
    "MemorySessionUser",
    "MemorySessionUserData",
    "lecture_page_memory",
    "MemoryLecturePage",
    "MemoryLecturePageData",
    "user_memory",
    "MemoryUser",
]

from obb.tools.MemDb import MemDb

from .blackboard_room import MemoryBlackboardRoom, MemoryBlackboardRoomData
from .user_session import MemorySessionUser, MemorySessionUserData
from .lecture_page import MemoryLecturePage, MemoryLecturePageData
from .user import MemoryUser

room_memory = MemDb[str, MemoryBlackboardRoom]()

user_memory = MemDb[str, MemoryUser]()

user_session_memory = MemDb[str, MemorySessionUser]()

lecture_page_memory = MemDb[str, MemoryLecturePage]()
