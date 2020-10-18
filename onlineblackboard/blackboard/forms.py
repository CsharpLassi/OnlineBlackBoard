from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ConnectToRoom(FlaskForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Join')


class CreateRoomForm(FlaskForm):
    room_name = StringField('Room', validators=[DataRequired(), Length(max=16)])
    submit = SubmitField('Create')
