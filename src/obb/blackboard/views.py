from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from flask_login import login_required, current_user

from ..ext import db

from .ext import namespace, bb_session_manager
from .decorators import check_room
from .models import BlackboardRoom

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import ConnectToRoom
    form = ConnectToRoom()

    if form.validate_on_submit():
        room_name = form.room_name.data
        room = BlackboardRoom.get_by_name(room_name)
        if not room or not room.can_join():
            flash('room does not exist')
            return redirect(url_for('blackboard.home'))

        session['room_name'] = room_name

        bb_session = bb_session_manager.create_session(room_id=room.id)

        return redirect(
            url_for('blackboard.mode_blackboard', session=bb_session.to_token_string()))

    form.room_name.data = session.get('room_name')
    return render_template('blackboard/home.html', form=form)


@bp.route('/show', methods=['GET', 'POST'])
@check_room('blackboard.home')
def mode_blackboard(room: BlackboardRoom = None):
    return render_template('blackboard/mode_blackboard.html', room=room)


@bp.route('/connectTo', methods=['GET', 'POST'])
@login_required
def connect_to():
    from .forms import CreateRoomForm

    create_form = CreateRoomForm()
    if create_form.validate_on_submit():
        room_name = create_form.room_name.data
        room_full_name = f'{current_user.username}.{room_name}'

        room = BlackboardRoom.get_by_name(room_full_name)
        if room:
            flash('Room already exist')
            return redirect(url_for('blackboard.connect_to'))

        room = BlackboardRoom()
        room.name = room_name
        room.full_name = room_full_name
        room.creator = current_user
        room.visibility = create_form.visibility.data

        db.session.add(room)
        db.session.commit()

        return redirect(url_for('blackboard.connect_to_room', room_id=room.id))

    rooms = BlackboardRoom.get_rooms()
    return render_template('blackboard/connect_to.html',
                           create_form=create_form,
                           rooms=rooms)


@bp.route('/connectTo/<room_id>', methods=['GET', 'POST'])
@login_required
def connect_to_room(room_id: str):
    room = BlackboardRoom.get(room_id)
    if not room or not room.can_join():
        flash('room does not exist')
        return redirect(url_for('blackboard.connect_to'))

    bb_session = bb_session_manager.create_session(room_id=room.id)

    return redirect(
        url_for('blackboard.mode_user', session=bb_session.to_token_string()))


@bp.route('/link', methods=['GET', 'POST'])
@login_required
@check_room('blackboard.connect_to')
def mode_user(room: BlackboardRoom):
    from .forms import RoomSettings

    edit_form = RoomSettings()
    if edit_form.validate_on_submit():
        room.draw_height = int(edit_form.height.data)
        room.visibility = edit_form.visibility.data
        db.session.commit()
        return redirect(url_for('blackboard.link_to', room_id=room.id))
    else:
        edit_form.height.data = room.draw_height
        edit_form.visibility.data = room.visibility

    return render_template('blackboard/mode_user.html', room=room, edit_form=edit_form)
