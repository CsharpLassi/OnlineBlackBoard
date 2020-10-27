import datetime

from flask import flash, redirect, url_for, render_template, request
from flask_login import login_required, current_user

from . import bp
from ..forms.lecture import ShortCreateLectureForm
from ..forms.room import ShortCreateRoomForm, CreateRoomForm
from ..models import BlackboardRoom, LectureSession, Lecture
from ...ext import db


@bp.route("/room", methods=["GET", "POST"])
@login_required
def room_list():
    create_room_form = ShortCreateRoomForm()
    create_lecture_form = ShortCreateLectureForm()

    rooms = BlackboardRoom.get_rooms()
    lectures = Lecture.get_lectures()

    # Todo: Query ?
    lecture_sessions = [
        l_session
        for l_session in LectureSession.get_lectures(current_user.id)
        if l_session.end_time > datetime.datetime.utcnow()
    ]

    return render_template(
        "blackboard/rooms.html",
        create_room_form=create_room_form,
        create_lecture_form=create_lecture_form,
        rooms=rooms,
        lectures=lectures,
        lecture_sessions=lecture_sessions,
    )


@bp.route("/room/create", methods=["GET", "POST"])
@login_required
def room_create():
    def render(create_form):
        return render_template("blackboard/room/create.html", create_form=create_form)

    create_form = CreateRoomForm()

    if create_form.validate_on_submit():
        room_name = create_form.room_name.data

        room = BlackboardRoom.get_by_name(room_name)
        if room:
            flash("Room already exist")
            return render(create_form)

        room = BlackboardRoom()
        room.name = room_name
        room.creator = current_user
        room.visibility = create_form.visibility.data

        db.session.add(room)
        db.session.commit()

        return redirect(url_for("blackboard.room_list"))

    return render(create_form)
