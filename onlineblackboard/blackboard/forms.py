from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateSessionForm(FlaskForm):
    room_id = StringField('ID', validators=[DataRequired(), Length(min=6, max=10)])
    submit = SubmitField('Create Session')


class ConnectForm(FlaskForm):
    room_id = StringField('ID', validators=[DataRequired(), Length(min=6, max=10)])
    submit = SubmitField('Connect')
