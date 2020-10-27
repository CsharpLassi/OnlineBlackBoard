from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

from obb.tools.forms import BaseDataForm


class ShortCreateLectureForm(FlaskForm, BaseDataForm):
    lecture_name = StringField("Lecture", validators=[DataRequired(), Length(max=16)])
    submit = SubmitField("Create")


class CreateLectureForm(FlaskForm, BaseDataForm):
    lecture_name = StringField("Lecture", validators=[DataRequired(), Length(max=16)])
    submit = SubmitField("Create")
