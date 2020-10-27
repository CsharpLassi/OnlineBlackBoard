from flask import flash, redirect, url_for, render_template, request
from flask_login import current_user, login_required

from . import bp
from ..forms import RoomSettingsForm
from ..models import BlackboardRoom
from ..memory import user_memory, MemoryUser
from ...api import ApiToken
from ...ext import db


@bp.route("/link/", methods=["GET", "POST"])
@bp.route("/link/blackboard", methods=["GET", "POST"])
def link_blackboard():
    room_id = request.args.get("r")

    room = BlackboardRoom.get(room_id)
    if not room:
        flash("room does not exist")
        return redirect("blackboard.home")

    l_session = room.get_current_lecture_session()
    if not l_session:
        flash("room is closed")
        return redirect("blackboard.home")

    token = ApiToken.create_token()

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

    token = ApiToken.create_token()

    memory_user = user_memory.add(token.sid, MemoryUser(token.sid, token.user_id))
    memory_user.mode = "user"
    memory_user.allow_draw = True
    memory_user.allow_new_page = True

    return render_template(
        "blackboard/mode_user.html",
        l_session=l_session,
        room=room,
        token=token,
        edit_form=edit_form,
    )
