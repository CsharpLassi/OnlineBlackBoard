import datetime
from typing import TypeVar, Optional, Iterator

# noinspection PyTypeChecker
from flask_login import current_user

BS = TypeVar("BS", bound="BlackboardRoom")

# noinspection PyTypeChecker
LS = TypeVar("LS", bound="LectureSession")


class BlackboardRoomWrapper:
    def get_current_lecture_session(self: BS) -> Optional[LS]:
        """
        :rtype: Optional[LectureSession]
        """
        from ..lecture_session import LectureSession

        lecture: LectureSession
        for lecture in self.sessions:
            if lecture.is_open():
                return lecture

        return None

    def intersect_lecture(self, start_time: datetime.datetime, duration: int) -> bool:
        from ..lecture_session import LectureSession

        end_time: datetime.datetime = start_time + datetime.timedelta(minutes=duration)
        lecture: LectureSession

        for lecture in self.sessions:
            if lecture.start_time < start_time < lecture.end_time:
                return True

            if lecture.start_time < end_time < lecture.end_time:
                return True

            if start_time < lecture.start_time < end_time:
                return True

            if start_time < lecture.end_time < end_time:
                return True

        return False

    @staticmethod
    def get_by_name(name: str, user=None) -> Optional[BS]:
        from ..blackboard_room import BlackboardRoom

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        if not user:
            return None

        query = BlackboardRoom.query

        query = query.filter_by(creator_id=user.id, is_invisible=False)

        query = query.filter_by(name=name)

        if query.count() != 1:
            return None

        return query.first()

    @staticmethod
    def get_rooms(user=None) -> Iterator[BS]:
        from flask_login import current_user
        from ..blackboard_room import BlackboardRoom
        from obb.users.models import User

        if isinstance(user, int):
            user = User.get(user)

        if not user and current_user and current_user.is_authenticated:
            user = current_user

        user_id = 0 if not user else user.id

        f_query = BlackboardRoom.query
        f_query = f_query.filter_by(is_invisible=False)

        f_query = f_query.filter(BlackboardRoom.creator_id == user_id)

        return f_query.all()
