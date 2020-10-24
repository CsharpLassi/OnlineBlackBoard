from typing import Optional

from ..components.page_manager import PageSession
from ..components.session_manager import BlackBoardSession
from ..ext import page_manager
from ..models import Lecture, BlackboardRoom


def get_page_session(session: BlackBoardSession, room: BlackboardRoom, msg_page=None) \
        -> Optional[PageSession]:
    lecture: Optional[Lecture] = Lecture.get(session.lecture_id)

    if not lecture:
        l_session = room.get_current_lecture_session()
        lecture = l_session.lecture

    if not lecture:
        return None

    page_id = msg_page or session.page_id or lecture.current_page_id or lecture.start_page_id

    page_session = page_manager.get(page_id, lecture=lecture,
                                    width=room.draw_width, height=room.draw_height)
    return page_session
