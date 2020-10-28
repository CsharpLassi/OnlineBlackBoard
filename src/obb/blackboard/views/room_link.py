from flask import flash, redirect, url_for, render_template, request, session
from flask_login import current_user, login_required

from . import bp
from ..forms.room import RoomSettingsForm
from ..models import BlackboardRoom
from ..memory import user_session_memory, MemorySessionUser, MemoryUser, user_memory
from ...api import ApiToken
from ...ext import db
from ...tools import id_generator
from ...users.models import User


def get_mem_user_session(room: BlackboardRoom):
    mem_user: MemoryUser = user_memory.get(session.get("user_id", None))
    if not mem_user:
        mem_user = MemoryUser()
        user_memory.add(mem_user.id, mem_user)
        session["user_id"] = mem_user.id

    mem_user_session_id = mem_user.sessions.get(room.id)
    mem_user_session = user_session_memory.get(mem_user_session_id)

    sid = mem_user_session_id or id_generator(24)
    if not mem_user_session:
        mem_user_session = MemorySessionUser(sid, User.get_current_id())
        user_session_memory.add(sid, mem_user_session)
        mem_user.sessions[room.id] = sid

    return mem_user_session


@bp.route("/link/", methods=["GET", "POST"])
@bp.route("/link/blackboard", methods=["GET", "POST"])
def link_blackboard():
    room_id = request.args.get("r")

    room = BlackboardRoom.get(room_id)
    if not room:
        flash("room does not exist")
        return redirect(url_for("blackboard.home"))

    l_session = room.get_current_lecture_session()
    if not l_session:
        flash("room is closed")
        return redirect(url_for("blackboard.home"))

    mem_user_session = get_mem_user_session(room)

    token = ApiToken.create_token(sid=mem_user_session.sid)

    return render_template(
        "blackboard/mode_blackboard.html", l_session=l_session, room=room, token=token
    )


@bp.route("/link/user", methods=["GET", "POST"])
@login_required
def link_user():
    room_id = request.args.get("r")
    room = BlackboardRoom.get(room_id)

    if room is None:
        flash("Room does not exist")
        return redirect(url_for("blackboard.room_list"))

    l_session = room.get_current_lecture_session()
    if not l_session:
        flash("room is closed")
        return redirect("blackboard.home")

    if room.creator_id != current_user.id:
        flash("you have no access to the page")
        return redirect(url_for("blackboard.room_list"))

    edit_form = RoomSettingsForm()

    if edit_form.validate_on_submit():
        edit_form.write_data(room)
        db.session.commit()
        return redirect(url_for("blackboard.link_user", room_id=room.id))

    edit_form.read_data(room)

    mem_user_session = get_mem_user_session(room)

    mem_user_session.mode = "user"
    mem_user_session.allow_draw = True
    mem_user_session.allow_new_page = True

    token = ApiToken.create_token(sid=mem_user_session.sid)

    return render_template(
        "blackboard/mode_user.html",
        l_session=l_session,
        room=room,
        token=token,
        edit_form=edit_form,
    )
