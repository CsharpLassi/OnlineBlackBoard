import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length

from obb.tools.forms import BaseDataForm


class CreateSessionForm(FlaskForm, BaseDataForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=128)])

    room_name = StringField("Room", validators=[DataRequired()])

    start_time = DateTimeField(
        "Start DateTime", default=datetime.datetime.now, validators=[DataRequired()]
    )
    duration = IntegerField("Duration", default=100, validators=[DataRequired()])

    lecture_name = StringField("Lecture", validators=[DataRequired()])

    submit = SubmitField("Create")
