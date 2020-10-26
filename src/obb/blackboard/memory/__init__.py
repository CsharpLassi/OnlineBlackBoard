__all__ = ['room_memory', 'MemoryBlackboardRoom', 'MemoryBlackboardRoomData',
           'user_memory', 'MemoryUser', 'MemoryUserData',
           'lecture_page_memory', 'MemoryLecturePage', 'MemoryLecturePageData']

from obb.tools.MemDb import MemDb

from .blackboard_room import MemoryBlackboardRoom, MemoryBlackboardRoomData
from .user import MemoryUser, MemoryUserData
from .lecture_page import MemoryLecturePage, MemoryLecturePageData

room_memory = MemDb[str, MemoryBlackboardRoom]()
user_memory = MemDb[str, MemoryUser]()
lecture_page_memory = MemDb[str, MemoryLecturePage]()
