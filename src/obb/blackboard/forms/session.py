import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired

from obb.tools.forms import BaseDataForm


class CreateSessionForm(FlaskForm, BaseDataForm):
    name = StringField("Name", validators=[DataRequired()])

    room_name = StringField("Room", validators=[DataRequired()])

    start_time = DateTimeField(
        "Start DateTime", default=datetime.datetime.now, validators=[DataRequired()]
    )
    duration = IntegerField("Duration", default=100, validators=[DataRequired()])

    lecture_name = StringField("Lecture", validators=[DataRequired()])

    submit = SubmitField("Create")
