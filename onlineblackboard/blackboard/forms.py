from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class CreateSessionForm(FlaskForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Create Room')


class ConnectForm(FlaskForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Connect to')
