from typing import Optional, TypeVar, Type

# noinspection PyTypeChecker
T = TypeVar("T", bound="BlackboardRoom")
# noinspection PyTypeChecker
LS = TypeVar("LS", bound="LectureSession")


class BlackboardRoomWrapper:
    def get_current_lecture_session(self: T) -> Optional[LS]:
        """
        :rtype: Optional[LectureSession]
        """
        from .models import LectureSession

        lecture: LectureSession
        for lecture in self.lecture_sessions:
            if lecture.is_open():
                return lecture

        return None
