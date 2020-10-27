from typing import Optional

from obb.blackboard.models import LectureSession, BlackboardRoom


def get_current_lecture_session(room: BlackboardRoom) -> Optional[LectureSession]:
    lecture: LectureSession
    for lecture in room.lecture_sessions:
        if lecture.is_open():
            return lecture

    return None
