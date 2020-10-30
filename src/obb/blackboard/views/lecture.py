from flask import flash, redirect, url_for, render_template, send_file, request
from flask_login import login_required, current_user

from . import bp
from ..forms.lecture import CreateLectureForm
from ..models import Lecture, BlackboardRoom, LecturePage, LectureSession
from ...ext import db


@bp.route("/lecture/create", methods=["GET", "POSt"])
@login_required
def lecture_create():
    def render(create_form):
        return render_template(
            "blackboard/lecture/create.html", create_form=create_form
        )

    create_form = CreateLectureForm()

    if create_form.validate_on_submit():
        lecture_name = create_form.lecture_name.data

        lecture = Lecture.get_by_name(lecture_name)
        if lecture:
            flash("Lecture already exist", "error")
            return render(create_form)

        lecture = Lecture()
        lecture.name = lecture_name
        lecture.creator = current_user

        lecture_page = LecturePage.create(lecture)

        db.session.add(lecture)
        db.session.add(lecture_page)
        db.session.commit()

        return redirect(url_for("blackboard.room_list"))

    return render(create_form)


@bp.route("/lecture/<lecture_id>", methods=["GET", "POSt"])
@login_required
def lecture_edit(lecture_id):
    lecture = Lecture.get(lecture_id)

    if lecture.creator != current_user:
        flash("Not allowed")
        return redirect(url_for("blackboard.room_list"))

    if not lecture:
        flash("lecture not found")
        return redirect(url_for("blackboard.home"))

    room_id = request.args.get("r")
    room = BlackboardRoom.get(room_id)
    if not room:
        room = lecture.edit_room
        if not room:
            room = BlackboardRoom()
            room.name = f"LectureRoom.{lecture.name}"
            room.creator = current_user
            room.is_invisible = True
            lecture.edit_room = room
            db.session.add(room)
            db.session.commit()

    current_session = room.get_current_lecture_session()
    if not current_session:
        current_session = LectureSession()
        current_session.name = f"Edit Session for {lecture.name}"
        current_session.visibility = "creator_only"
        current_session.room = room
        current_session.lecture = lecture
        current_session.maintainer = current_user
        db.session.add(current_session)
        db.session.commit()

    return redirect(url_for("blackboard.link_user", room_id=room.id))


@bp.route("/lecture/<lecture_id>/download", methods=["GET", "POSt"])
@login_required
def lecture_download(lecture_id: int):
    lecture = Lecture.get(lecture_id)
    if current_user != lecture.creator:
        return

    fname, fpath = lecture.create_export_file()
    return send_file(
        fpath, attachment_filename=fname, as_attachment=True, mimetype="application/zip"
    )
