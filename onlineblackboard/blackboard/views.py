from flask import Blueprint, render_template, redirect, url_for
from flask_socketio import rooms

from .config import namespace

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    return render_template('blackboard/home.html')


@bp.route('connect_to', methods=['GET', 'POST'])
def connect_to():
    from .forms import ConnectForm
    connect_form = ConnectForm()
    if connect_form.validate_on_submit():
        room_id = connect_form.room_id.data
        return redirect(url_for('blackboard.link_to', room_id=room_id))
    return render_template('blackboard/connect_to.html', connect_form=connect_form)


@bp.route('link/<room_id>', methods=['GET'])
def link_to(room_id: str):
    return render_template('blackboard/link_to.html', room_id=room_id)
