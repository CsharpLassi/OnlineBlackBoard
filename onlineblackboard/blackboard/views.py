from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import login_required

from .ext import namespace, room_db
from .functions import id_generator
from .server_models import BlackboardRoom
from .decorators import check_room

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import CreateSessionForm
    form = CreateSessionForm()

    if form.validate_on_submit():
        room_name = form.room_name.data
        room_id = BlackboardRoom.get_hash(room_name)

        room = room_db.get(room_id)
        if room is None:
            room = BlackboardRoom(room_name)
            room_db.add(room_id, room)

            session['room_name'] = room_name

        return redirect(
            url_for('blackboard.mode_blackboard', room_id=room_id))

    room_name = session.get('room_name')

    if room_name is None:
        room_name = id_generator()
        session['room_name'] = room_name

    form.room_name.data = room_name
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
        room_id = connect_form.room_name.data
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
