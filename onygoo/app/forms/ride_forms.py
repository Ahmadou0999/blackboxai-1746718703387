from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class RideForm(FlaskForm):
    origin = StringField('Origin', validators=[DataRequired(), Length(max=255)])
    destination = StringField('Destination', validators=[DataRequired(), Length(max=255)])
    departure_time = DateTimeField('Departure Time', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    seats_available = IntegerField('Seats Available', validators=[DataRequired(), NumberRange(min=1)])
    price_per_seat = FloatField('Price per Seat', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Propose Ride')
