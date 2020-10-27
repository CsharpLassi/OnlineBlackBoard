from typing import Optional

from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from . import bp
from ..forms.session import CreateSessionForm
from ..models import BlackboardRoom, LectureSession, Lecture, LecturePage
from ...ext import db


@bp.route("/session/create", methods=["GET", "POST"])
@login_required
def session_create():
    def render(form, rooms, lectures):
        return render_template(
            "blackboard/session/create.html", form=form, rooms=rooms, lectures=lectures
        )

    rooms = BlackboardRoom.get_rooms()
    lectures = Lecture.get_lectures()

    form = CreateSessionForm()
    if form.validate_on_submit():

        room = BlackboardRoom.get_by_name(form.room_name.data)
        lecture = Lecture.get_by_name(form.lecture_name.data)

        fail_count = 0

        if not room:
            flash("room does not exist")
            fail_count += 1

        if not lecture:
            flash("lecture does not exist")
            fail_count += 1

        if fail_count:
            return render(form, rooms, lectures)

        lecture_session = LectureSession()
        lecture_session.maintainer = current_user
        form.write_data(lecture_session)

        lecture_session.lecture = lecture
        lecture_session.room = room

        db.session.add(lecture_session)

        if room.intersect_lecture(lecture_session.start_time, lecture_session.duration):
            flash("Session intersects")
            return render(form, rooms, lectures)

        room.sessions.append(lecture_session)

        db.session.commit()

        return redirect(url_for("blackboard.room_list"))

    return render(form, rooms, lectures)
