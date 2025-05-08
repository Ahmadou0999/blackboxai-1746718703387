from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

class ReservationForm(FlaskForm):
    ride_id = IntegerField('Ride ID', validators=[DataRequired()])
    submit = SubmitField('Book Seat')
