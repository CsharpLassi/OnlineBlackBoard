import datetime

from flask import render_template

from . import bp
from ..models import LectureSession


@bp.route('/', methods=['GET', 'POST'])
def home():
    l_sessions = [l_session for l_session in
                LectureSession.get_lectures()
                if l_session.end_time > datetime.datetime.utcnow()
                if l_session.is_open()]

    return render_template('blackboard/home.html', l_sessions=l_sessions)
