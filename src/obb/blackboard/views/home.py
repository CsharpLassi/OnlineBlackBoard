import datetime

from flask import render_template

from . import bp
from ..models import LectureSession


@bp.route('/', methods=['GET', 'POST'])
def home():
    lectures = [lecture for lecture in
                LectureSession.get_lectures()
                if lecture.end_time > datetime.datetime.utcnow()
                if lecture.is_open() and lecture.room.can_join()]

    return render_template('blackboard/home.html', lectures=lectures)
