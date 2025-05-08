from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')

class ProfilePhotoForm(FlaskForm):
    photo = FileField('Profile Photo', validators=[DataRequired()])
    submit = SubmitField('Upload Photo')
