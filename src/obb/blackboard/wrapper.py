from typing import Optional, TypeVar, Type

# noinspection PyTypeChecker
BS = TypeVar("BS", bound="BlackboardRoom")
# noinspection PyTypeChecker
L = TypeVar("L", bound="Lecture")
# noinspection PyTypeChecker
LS = TypeVar("LS", bound="LectureSession")
# noinspection PyTypeChecker
LP = TypeVar("LP", bound="LecturePage")


class BlackboardRoomWrapper:
    def get_current_lecture_session(self: BS) -> Optional[LS]:
        """
        :rtype: Optional[LectureSession]
        """
        from .models import LectureSession

        lecture: LectureSession
        for lecture in self.sessions:
            if lecture.is_open():
                return lecture

        return None


class LectureWrapper:
    @property
    def start_page(self: L) -> Optional[LP]:
        from .models import LecturePage

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(LecturePage.id)

        return query.first()

    @property
    def current_page(self: L) -> Optional[LP]:
        from .models import LecturePage

        query = LecturePage.query.filter_by(lecture_id=self.id).order_by(
            LecturePage.id.desc()
        )

        return query.first()
