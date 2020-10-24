from typing import Optional

from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from . import bp
from ..forms import CreateSession
from ..models import BlackboardRoom, LectureSession, Lecture
from ...ext import db


@bp.route('/session/create', methods=['GET', 'POST'])
@login_required
def session_create():
    def render(form, rooms, lectures):
        return render_template('blackboard/session/create.html',
                               form=form,
                               rooms=rooms,
                               lectures=lectures)

    room: Optional[BlackboardRoom] = None
    if room_id := request.args.get('room_id'):
        room = BlackboardRoom.get(room_id)
        # Todo: Check Access

    rooms = BlackboardRoom.get_rooms(usable=True)
    lectures = Lecture.get_lectures()

    form = CreateSession()
    if form.validate_on_submit():

        room = BlackboardRoom.get_by_name(form.room_name.data)
        lecture = Lecture.get_by_name(form.room_name.data)

        if form.new_room.data and room:
            flash('room already exist')
            return render(form, rooms, lectures)
        elif form.new_room.data:
            room = BlackboardRoom()
            room.name = form.name.data
            room.full_name = f'{current_user.username}.{room.name}'
            room.creator = current_user

        if form.new_lecture.data and lecture:
            flash('lecture already exist')
            return render(form, rooms, lectures)
        elif form.new_lecture.data:
            lecture = Lecture()
            lecture.name = form.lecture_name.data
            lecture.full_name = f'{current_user.username}.{lecture.name}'
            lecture.creator = current_user

        lecture_session = LectureSession()
        lecture_session.maintainer = current_user
        form.write_data(lecture_session)

        lecture_session.lecture = lecture
        lecture_session.room = room

        if room.intersect_lecture(lecture_session.start_time, lecture_session.duration):
            flash('Session intersects')
            return render(form, rooms, lectures)

        room.lecture_sessions.append(lecture_session)
        db.session.commit()

        return redirect(url_for('blackboard.room_list'))

    if room:
        form.room_name.data = room.full_name

    return render(form, rooms, lectures)
