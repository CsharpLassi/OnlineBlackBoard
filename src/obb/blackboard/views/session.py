from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from . import bp
from ..forms import CreateSession
from ..models import BlackboardRoom, LectureSession, Lecture
from ...ext import db


@bp.route('/session/create', methods=['GET', 'POST'])
@login_required
def session_create():
    room: BlackboardRoom
    if room_id := request.args.get('room_id'):
        room = BlackboardRoom.get(room_id)
        # Todo: Check Access

    form = CreateSession()
    if form.validate_on_submit():
        lecture_session = LectureSession()
        lecture_session.maintainer = current_user
        form.write_data(lecture_session)

        if form.new_lecture.data:
            new_lecture = Lecture()
            new_lecture.name = form.name.data
            new_lecture.creator = current_user

            lecture_session.lecture = new_lecture
        else:
            flash('No lecture found')
            return render_template('blackboard/create_session.html', form=form)

        if room.intersect_lecture(lecture_session.start_time, lecture_session.duration):
            flash('Session intersects')
            return render_template('blackboard/create_session.html', form=form)

        room.lecture_sessions.append(lecture_session)
        db.session.commit()

        return redirect(url_for('blackboard.list_rooms'))

    return render_template('blackboard/create_session.html', form=form)
