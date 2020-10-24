from flask import flash, redirect, url_for, render_template
from flask_login import current_user, login_required

from . import bp
from ..ext import bb_session_manager
from ..forms import RoomSettings
from ..models import BlackboardRoom
from ...ext import db


@bp.route('/link/<room_id>/blackboard', methods=['GET', 'POST'])
def link_blackboard(room_id: str):
    room = BlackboardRoom.get(room_id)
    if not room:
        flash('room does not exist')
        return redirect('blackboard.home')

    if not room.can_join():
        flash('not allowed')
        return redirect(url_for('blackboard.home'))

    bb_session = bb_session_manager.create_session(room_id=room.id)

    bb_session.session_user_data.mode = 'blackboard'
    return render_template('blackboard/mode_blackboard.html',
                           room=room,
                           bb_session=bb_session)


@bp.route('/link/<room_id>/user', methods=['GET', 'POST'])
@login_required
def link_user(room_id: str):
    room = BlackboardRoom.get(room_id)

    if room is None:
        flash('Room does not exist')
        return redirect(url_for('blackboard.list_rooms'))

    if not room.can_join():
        flash('room is closed')
        return redirect(url_for('blackboard.list_rooms'))

    if room.creator_id != current_user.id:
        flash('you have no access to the page')
        return redirect(url_for('blackboard.list_rooms'))

    edit_form = RoomSettings()

    if edit_form.validate_on_submit():
        edit_form.write_data(room)
        db.session.commit()
        return redirect(url_for('blackboard.link_user', room_id=room.id))

    edit_form.read_data(room)

    bb_session = bb_session_manager.create_session(room_id=room.id)
    bb_session.session_user_data.mode = 'user'
    bb_session.session_user_data.allow_draw = True
    bb_session.session_user_data.allow_new_page = True

    return render_template('blackboard/mode_user.html',
                           room=room,
                           bb_session=bb_session,
                           edit_form=edit_form)
