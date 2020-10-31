from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length

from obb.blackboard.models.defaults import Visibility, default_blackboard_visibility
from obb.tools.forms import BaseDataForm


class ShortCreateRoomForm(FlaskForm, BaseDataForm):
    room_name = StringField("Room", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("Create")


class CreateRoomForm(FlaskForm, BaseDataForm):
    room_name = StringField("Room", validators=[DataRequired(), Length(max=128)])
    visibility = SelectField(
        "Visibility",
        default=default_blackboard_visibility,
        choices=Visibility.list(),
        validators=[DataRequired()],
    )
    submit = SubmitField("Create")


class RoomSettingsForm(FlaskForm, BaseDataForm):
    draw_height = IntegerField("Board-Height", validators=[DataRequired()])
    draw_width = IntegerField("Board-Width", validators=[DataRequired()])
    visibility = SelectField(
        "Visibility",
        default=default_blackboard_visibility,
        choices=Visibility.list(),
        validators=[DataRequired()],
    )
    submit = SubmitField("Update")
