from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length
from .models import default_visibility, blackboardRoom_visibilities

from obb.tools.forms import BaseDataForm


class ConnectToRoom(FlaskForm, BaseDataForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Join')


class CreateRoomForm(FlaskForm, BaseDataForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])  #
    visibility = SelectField('Visibility',
                             default=default_visibility,
                             choices=blackboardRoom_visibilities,
                             validators=[DataRequired()])
    submit = SubmitField('Create')


class RoomSettings(FlaskForm, BaseDataForm):
    draw_height = IntegerField('Board-Height')
    visibility = SelectField('Visibility',
                             default=default_visibility,
                             choices=blackboardRoom_visibilities,
                             validators=[DataRequired()])
    submit = SubmitField('Update')
