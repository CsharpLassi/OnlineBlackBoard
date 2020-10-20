import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length
from .models import default_visibility, blackboardRoom_visibilities

from obb.tools.forms import BaseDataForm


class ConnectToRoom(FlaskForm, BaseDataForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Join')


class CreateRoomForm(FlaskForm, BaseDataForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    visibility = SelectField('Visibility',
                             default=default_visibility,
                             choices=blackboardRoom_visibilities,
                             validators=[DataRequired()])
    submit = SubmitField('Create')


class RoomSettings(FlaskForm, BaseDataForm):
    draw_height = IntegerField('Board-Height', validators=[DataRequired()])
    draw_width = IntegerField('Board-Width', validators=[DataRequired()])
    visibility = SelectField('Visibility',
                             default=default_visibility,
                             choices=blackboardRoom_visibilities,
                             validators=[DataRequired()])
    submit = SubmitField('Update')


class CreateSession(FlaskForm, BaseDataForm):
    start_time = DateTimeField('Start DateTime',
                               default=datetime.datetime.now,
                               validators=[DataRequired()])
    duration = IntegerField('Duration', default=100, validators=[DataRequired()])
    submit = SubmitField('Create')
