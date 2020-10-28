import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint

bp = Blueprint("blackboard.cron", __name__)


def work_user_session_memory():
    from .memory import user_session_memory

    for item in user_session_memory.pop_expired():
        item.clear_temp_data()


def work_session_memory():
    from .memory import user_session_memory

    for item in user_session_memory.pop_expired():
        item.clear_temp_data()


def work_lecture_page_memory():
    from .memory import user_session_memory

    for item in user_session_memory.pop_expired():
        item.clear_temp_data()


def work_room_memory():
    from .memory import user_session_memory

    for item in user_session_memory.pop_expired():
        item.clear_temp_data()


@bp.before_app_first_request
def create_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(work_user_session_memory, "interval", minutes=1)
    scheduler.add_job(work_session_memory, "interval", minutes=1)
    scheduler.add_job(work_lecture_page_memory, "interval", minutes=1)
    scheduler.add_job(work_room_memory, "interval", minutes=1)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
