from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from flask_login import login_required, current_user

from ..ext import db

from .ext import namespace, bb_session_manager
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

        return redirect(
            url_for('blackboard.link', room_id=room.id))

    rooms = BlackboardRoom.get_rooms(public=True)
    form.room_name.data = session.get('room_name')
    return render_template('blackboard/home.html', form=form, rooms=rooms)


@bp.route('/link/<room_id>', methods=['GET', 'POST'])
def link(room_id: str):
    room = BlackboardRoom.get(room_id)
    if not room:
        flash('room does not exist')
        return redirect('blackboard.home')

    if not room.can_join():
        flash('not allowed')
        return redirect('blackboard.home')

    bb_session = bb_session_manager.create_session(room_id=room.id)

    if current_user and current_user.is_authenticated:
        if current_user.id == room.creator_id:
            return redirect(url_for('blackboard.link_user', room_id=room.id))

    return render_template('blackboard/mode_blackboard.html',
                           room=room,
                           bb_session=bb_session)


@bp.route('/linkUser/<room_id>', methods=['GET', 'POST'])
@login_required
def link_user(room_id: str):
    from .forms import RoomSettings

    room = BlackboardRoom.get(room_id)

    if room is None:
        flash('Room does not exist')
        return redirect(url_for('blackboard.home'))

    if room.creator_id != current_user.id:
        flash('you have no access to the page')
        return redirect(url_for('blackboard.home'))

    edit_form = RoomSettings()

    if edit_form.validate_on_submit():
        edit_form.write_data(room)
        db.session.commit()
        return redirect(url_for('blackboard.link_user', room_id=room.id))

    edit_form.read_data(room)

    bb_session = bb_session_manager.create_session(room_id=room.id)
    return render_template('blackboard/mode_user.html',
                           room=room,
                           bb_session=bb_session,
                           edit_form=edit_form)


@bp.route('/rooms', methods=['GET', 'POST'])
@login_required
def list_rooms():
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

        return redirect(url_for('blackboard.link', room_id=room.id))

    rooms = BlackboardRoom.get_rooms()
    return render_template('blackboard/rooms.html',
                           create_form=create_form,
                           rooms=rooms)
