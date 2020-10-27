from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length

from obb.blackboard.models import default_visibility, blackboardRoom_visibilities
from obb.tools.forms import BaseDataForm


class CreateRoomForm(FlaskForm, BaseDataForm):
    room_name = StringField("Room", validators=[DataRequired(), Length(max=16)])
    visibility = SelectField(
        "Visibility",
        default=default_visibility,
        choices=blackboardRoom_visibilities,
        validators=[DataRequired()],
    )
    submit = SubmitField("Create")


class RoomSettingsForm(FlaskForm, BaseDataForm):
    draw_height = IntegerField("Board-Height", validators=[DataRequired()])
    draw_width = IntegerField("Board-Width", validators=[DataRequired()])
    visibility = SelectField(
        "Visibility",
        default=default_visibility,
        choices=blackboardRoom_visibilities,
        validators=[DataRequired()],
    )
    submit = SubmitField("Update")
