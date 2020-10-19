from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from flask_login import login_required, current_user

from ..ext import db

from .ext import namespace, bb_manager
from .functions import id_generator
from .server_models import BlackboardRoomSession
from .decorators import check_room
from .models import BlackboardRoom

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import ConnectToRoom
    form = ConnectToRoom()

    if form.validate_on_submit():
        room_name = form.room_name.data
        db_room = BlackboardRoom.get_active_room(room_name)
        if db_room is None:
            flash('room does not exist')
            return redirect(url_for('blackboard.home'))

        session['room_name'] = room_name

        room = room_db.get(db_room.id)
        if room is None:
            flash('room does not exist')
            return redirect(url_for('blackboard.home'))

        return redirect(
            url_for('blackboard.mode_blackboard', room_id=db_room.id))

    room_name = session.get('room_name')

    if room_name is None:
        room_name = id_generator()
        session['room_name'] = room_name

    form.room_name.data = room_name
    return render_template('blackboard/home.html', form=form)


@bp.route('/show', methods=['GET', 'POST'])
@check_room('blackboard.home')
def mode_blackboard(room: BlackboardRoomSession = None):
    return render_template('blackboard/mode_blackboard.html', room=room)


@bp.route('connectTo', methods=['GET', 'POST'])
@login_required
def connect_to():
    from .forms import CreateRoomForm

    create_form = CreateRoomForm()
    if create_form.validate_on_submit():
        room_name = create_form.room_name.data

        db_room = BlackboardRoom.get_active_room(room_name)
        if db_room is None:
            db_room = BlackboardRoom()
            db_room.name = room_name
            db_room.creator = current_user
            db_room.visibility = create_form.visibility.data

            db.session.add(db_room)
            db.session.commit()

        room = room_db.get(db_room.id, BlackboardRoomSession(db_room))

        return redirect(url_for('blackboard.link_to', room_id=room.room_id))

    rooms = BlackboardRoom.get_active_rooms()
    return render_template('blackboard/connect_to.html',
                           create_form=create_form,
                           rooms=rooms)


@bp.route('link', methods=['GET', 'POST'])
@login_required
@check_room('blackboard.connect_to', create_room_from_db=True)
def link_to(room: BlackboardRoomSession = None):
    from .forms import RoomSettings

    db_room = room.db_room

    edit_form = RoomSettings()
    if edit_form.validate_on_submit():
        db_room.draw_height = int(edit_form.height.data)
        db_room.visibility = edit_form.visibility.data
        db.session.commit()
        return redirect(url_for('blackboard.link_to', room_id=room.room_id))
    else:
        edit_form.height.data = db_room.draw_height

    return render_template('blackboard/mode_user.html', room=room, edit_form=edit_form)
