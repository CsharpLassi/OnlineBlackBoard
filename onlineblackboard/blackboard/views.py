from flask import Blueprint, render_template, redirect, url_for, session
from flask_socketio import rooms

from .ext import namespace, id_generator

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    from .forms import CreateSessionForm
    form = CreateSessionForm()

    if form.validate_on_submit():
        return redirect(
            url_for('blackboard.mode_blackboard', room_id=form.room_id.data))

    room_id = session.get('room_id')

    if room_id is None:
        room_id = id_generator()
        session['room_id'] = room_id

    form.room_id.data = room_id
    return render_template('blackboard/home.html', form=form)


@bp.route('/show', methods=['GET', 'POST'])
def mode_blackboard():
    return render_template('blackboard/mode_blackboard.html')


@bp.route('connectTo', methods=['GET', 'POST'])
def connect_to():
    from .forms import ConnectForm
    connect_form = ConnectForm()
    if connect_form.validate_on_submit():
        room_id = connect_form.room_id.data
        return redirect(url_for('blackboard.link_to', room_id=room_id))
    return render_template('blackboard/connect_to.html', connect_form=connect_form)


@bp.route('link', methods=['GET'])
def link_to():
    return render_template('blackboard/mode_user.html')
