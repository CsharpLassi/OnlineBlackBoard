from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required

from .ext import namespace, room_db
from .functions import id_generator
from .server_models import BlackboardRoom
from .messages import RoomCreatedData

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


def check_room(fallback: str, allow_closed_rooms: bool = False):
    def check_room_helper(func):
        @wraps(func)
        def room_checker(*args, **kwargs):
            room_id = request.args.get('room_id')
            if room_id is None or not room_db.exist(room_id):
                flash(f'room does not exist')
                return redirect(url_for(fallback))
            room: BlackboardRoom = room_db.get(room_id)

            if not allow_closed_rooms and room.closed:
                flash(f'Room is closed')
                return redirect(url_for(fallback))

            kwargs['room'] = room
            return func(*args, **kwargs)

        return room_checker

    return check_room_helper


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import CreateSessionForm
    from ..ext import socket
    form = CreateSessionForm()

    if form.validate_on_submit():
        room_id = form.room_id.data

        room = room_db.get(room_id)
        if room is None:
            room = BlackboardRoom(room_id)
            room_db.add(room_id, room)

            session['room_id'] = room_id

        return redirect(
            url_for('blackboard.mode_blackboard', room_id=form.room_id.data))

    room_id = session.get('room_id')

    if room_id is None:
        room_id = id_generator()
        session['room_id'] = room_id

    form.room_id.data = room_id
    return render_template('blackboard/home.html', form=form)


@bp.route('/show', methods=['GET', 'POST'])
@check_room('blackboard.home', allow_closed_rooms=True)
def mode_blackboard(room: BlackboardRoom = None):
    return render_template('blackboard/mode_blackboard.html')


@bp.route('connectTo', methods=['GET', 'POST'])
@login_required
def connect_to():
    from .forms import ConnectForm

    connect_form = ConnectForm()
    if connect_form.validate_on_submit():
        room_id = connect_form.room_id.data
        return redirect(url_for('blackboard.link_to', room_id=room_id))
    rooms = [room for room_id, room in room_db.items()]
    return render_template('blackboard/connect_to.html',
                           connect_form=connect_form,
                           rooms=rooms)


@bp.route('link', methods=['GET'])
@login_required
@check_room('blackboard.connect_to')
def link_to(room: BlackboardRoom = None):
    return render_template('blackboard/mode_user.html', room=room)
