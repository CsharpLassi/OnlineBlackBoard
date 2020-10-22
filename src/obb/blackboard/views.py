import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from ..ext import db

from .ext import namespace, bb_session_manager
from .models import BlackboardRoom, LectureSession, Lecture

bp = Blueprint('blackboard', __name__, url_prefix=namespace)


@bp.route('/', methods=['GET', 'POST'])
def home():
    lectures = [lecture for lecture in
                LectureSession.get_lectures()
                if lecture.end_time > datetime.datetime.utcnow()
                if lecture.is_open() and lecture.room.can_join()]

    return render_template('blackboard/home.html', lectures=lectures)


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
            return redirect(url_for('blackboard.list_rooms'))

        room = BlackboardRoom()
        room.name = room_name
        room.full_name = room_full_name
        room.creator = current_user
        room.visibility = create_form.visibility.data

        db.session.add(room)
        db.session.commit()

        return redirect(url_for('blackboard.list_rooms'))

    rooms = BlackboardRoom.get_rooms()

    lecture_sessions = [l_session for l_session in
                        LectureSession.get_lectures(current_user.id)
                        if l_session.end_time > datetime.datetime.utcnow()]

    return render_template('blackboard/rooms.html',
                           create_form=create_form,
                           rooms=rooms,
                           lecture_sessions=lecture_sessions)


@bp.route('/link/<room_id>', methods=['GET', 'POST'])
def link(room_id: str):
    mode = request.args.get('mode')

    room = BlackboardRoom.get(room_id)
    if not room:
        flash('room does not exist')
        return redirect('blackboard.home')

    if not room.can_join():
        flash('not allowed')
        return redirect(url_for('blackboard.home'))

    bb_session = bb_session_manager.create_session(room_id=room.id)

    if mode is None:
        if current_user and current_user.is_authenticated:
            if current_user.id == room.creator_id:
                return redirect(url_for('blackboard.link_user', room_id=room.id))

    bb_session.session_user_data.mode = 'blackboard'
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

    return render_template('blackboard/mode_user.html',
                           room=room,
                           bb_session=bb_session,
                           edit_form=edit_form)


@bp.route('/create/<room_id>', methods=['GET', 'POST'])
@login_required
def create_session(room_id: str):
    from .forms import CreateSession

    room = BlackboardRoom.get(room_id)
    if room is None:
        flash('room does not exist')
        return redirect(url_for('blackboard.list_rooms'))

    form = CreateSession()
    if form.validate_on_submit():
        lecture_session = LectureSession()
        lecture_session.maintainer = current_user
        form.write_data(lecture_session)

        if form.new_lecture.data:
            new_lecture = Lecture()
            new_lecture.name = form.name.data
            new_lecture.creator = current_user

            lecture_session.lecture = new_lecture
        else:
            flash('No lecture found')
            return redirect(url_for('blackboard.list_rooms'))

        if room.intersect_lecture(lecture_session.start_time, lecture_session.duration):
            flash('Session intersects')
            return redirect(url_for('blackboard.list_rooms'))

        room.lecture_sessions.append(lecture_session)
        db.session.commit()

        return redirect(url_for('blackboard.list_rooms'))

    return render_template('blackboard/create_session.html', form=form)
