from typing import Optional

from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from . import bp
from ..forms import CreateSessionForm
from ..models import BlackboardRoom, LectureSession, Lecture, LecturePage
from ...ext import db


@bp.route("/session/create", methods=["GET", "POST"])
@login_required
def session_create():
    def render(form, rooms, lectures):
        return render_template(
            "blackboard/session/create.html", form=form, rooms=rooms, lectures=lectures
        )

    room: Optional[BlackboardRoom] = None
    lecture: Optional[Lecture] = None

    room_id = request.args.get("room_id")
    lecture_id = request.args.get("lecture_id")

    if room_id:
        room = BlackboardRoom.get(room_id)

    if lecture_id:
        lecture = Lecture.get(lecture_id)

    rooms = BlackboardRoom.get_rooms(usable=True)
    lectures = Lecture.get_lectures()

    form = CreateSessionForm()
    if form.validate_on_submit():

        room = BlackboardRoom.get_by_name(form.room_name.data)
        lecture = Lecture.get_by_name(form.lecture_name.data)

        if form.new_room.data and room:
            flash("room already exist")
            return render(form, rooms, lectures)
        elif form.new_room.data:
            room = BlackboardRoom()
            room.name = form.name.data
            room.creator = current_user
            db.session.add(room)
        elif not room:
            flash("room does not exist")
            return render(form, rooms, lectures)

        if form.new_lecture.data and lecture:
            flash("lecture already exist")
            return render(form, rooms, lectures)
        elif form.new_lecture.data:
            lecture = Lecture()
            lecture.name = form.lecture_name.data
            lecture.creator = current_user

            start_page = LecturePage.create(lecture)

            lecture.pages.append(start_page)

            db.session.add(lecture)
            db.session.add(start_page)
        elif not lecture:
            flash("lecture does not exist")
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

    if room:
        form.room_name.data = room.name

    if lecture:
        form.lecture_name.data = lecture.name

    return render(form, rooms, lectures)
