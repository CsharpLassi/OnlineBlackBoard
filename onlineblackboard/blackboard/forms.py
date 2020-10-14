from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class ConnectForm(FlaskForm):
    room_id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Connect')
