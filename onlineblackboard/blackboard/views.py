from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import current_user, login_required

from .server_models import BlackboardRoom
from .ext import namespace, id_generator, room_db

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


def check_room(fallback: str):
    def check_room_helper(func):
        @wraps(func)
        def room_checker(*args, **kwargs):
            room_id = request.args.get('room_id')
            if room_id is None or not room_db.exist(room_id):
                flash(f'room does not exist')
                return redirect(url_for(fallback))
            return func(*args, **kwargs)

        return room_checker

    return check_room_helper


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import CreateSessionForm
    form = CreateSessionForm()

    if form.validate_on_submit():
        room_id = form.room_id.data

        room = room_db.get(room_id)
        if room is None:
            room = BlackboardRoom(room_id)
            room_db.add(room_id, room)

        return redirect(
            url_for('blackboard.mode_blackboard', room_id=form.room_id.data))

    room_id = session.get('room_id')

    if room_id is None:
        room_id = id_generator()
        session['room_id'] = room_id

    form.room_id.data = room_id
    return render_template('blackboard/home.html', form=form)


@bp.route('/show', methods=['GET', 'POST'])
@check_room('blackboard.home')
def mode_blackboard():
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
@check_room('blackboard.connect_to')
@login_required
def link_to():
    return render_template('blackboard/mode_user.html')
