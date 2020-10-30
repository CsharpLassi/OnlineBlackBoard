from flask import flash, redirect, url_for, render_template, send_file
from flask_login import login_required, current_user

from . import bp
from ..forms.lecture import CreateLectureForm
from ..memory import user_session_memory, MemorySessionUser
from ..models import Lecture, BlackboardRoom, LecturePage
from ...api import ApiToken
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
def lecture_show(lecture_id):
    def render(lecture, token):
        return render_template(
            "blackboard/lecture/show.html", token=token, lecture=lecture
        )

    lecture = Lecture.get(lecture_id)

    if not lecture:
        flash("lecture not found")
        return redirect(url_for("blackboard.home"))

    room = lecture.edit_room
    if not room:
        room = BlackboardRoom()
        room.name = f"LectureRoom.{lecture.name}"
        room.creator = current_user
        room.is_invisible = True
        lecture.edit_room = room
        db.session.commit()

    token = ApiToken.create_token()

    memory_user = user_session_memory.add(
        token.sid, MemorySessionUser(token.sid, token.user_id)
    )
    memory_user.mode = "user"
    memory_user.allow_draw = True
    memory_user.allow_new_page = True

    return render(lecture, token)


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
