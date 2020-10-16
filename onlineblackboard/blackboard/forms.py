from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateSessionForm(FlaskForm):
    room_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Create Session')


class ConnectForm(FlaskForm):
    room_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Connect')
