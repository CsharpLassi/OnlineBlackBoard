from flask import flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from . import bp
from ..ext import bb_session_manager
from ..models import Lecture, BlackboardRoom
from ...ext import db


@bp.route('/lecture/<lecture_id>', methods=['GET', 'POSt'])
@login_required
def lecture_show(lecture_id):
    def render(lecture, bb_session):
        return render_template('blackboard/lecture/show.html',
                               bb_session=bb_session,
                               lecture=lecture)

    lecture = Lecture.get(lecture_id)

    if not lecture:
        flash('lecture not found')
        return redirect(url_for('blackboard.home'))

    room = lecture.edit_room
    if not room:
        room = BlackboardRoom()
        room.name = f'LectureRoom.{lecture.name}'
        room.full_name = f'LectureRoom.{lecture.full_name}'
        room.creator = current_user
        room.is_invisible = True
        lecture.edit_room = room
        db.session.commit()

    bb_session = bb_session_manager.create_session(room_id=room.id)
    bb_session.session_user_data.mode = 'viewer'
    bb_session.session_user_data.allow_draw = False
    bb_session.lecture_id = lecture.id

    return render(lecture, bb_session)
