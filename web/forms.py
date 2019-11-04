from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, HiddenField, validators


class CredentialForm(FlaskForm):
    username = StringField('Username: ', validators=[validators.Length(min=1, max=30)])
    password = PasswordField('Password: ', validators=[validators.Length(min=1, max=30)])
    submit = SubmitField('Sign In')


class StartRideForm(FlaskForm):
    submit = SubmitField('Start ride')


class EndRideForm(FlaskForm):
    submit = SubmitField('End ride')


class VehicleForm(FlaskForm):
    city = SelectField('City: ',  choices=[('new york', 'New York'), ('boston', 'Boston'), ('washington dc', 'Washington DC'),
                ('san francisco', 'San Francisco'), ('seattle', 'Seattle'), ('los angeles', 'Los Angeles'),
                ('chicago', 'Chicago'), ('detroit', 'Detroit'), ('minneapolis', 'Minneapolis'),
                ('amsterdam', 'Amsterdam'), ('paris', 'Paris'), ('rome', 'Rome')])
    type = SelectField(label='Type', choices=[('bike', 'Bike'), ('scooter', 'Scooter'), ('skateboard', 'Skateboard')])
    color = StringField(label='Color', validators=[validators.Length(min=1, max=15)])
    brand = StringField(label='Brand', validators=[validators.Length(min=1, max=10)])
    location = StringField(label='Current location: ', validators=[validators.Length(min=1, max=50)])
    submit = SubmitField('Add vehicle')


class RegisterForm(FlaskForm):
    city = SelectField('City: ',  choices=[('new york', 'New York'), ('boston', 'Boston'), ('washington dc', 'Washington DC'),
                ('san francisco', 'San Francisco'), ('seattle', 'Seattle'), ('los angeles', 'Los Angeles'),
                ('chicago', 'Chicago'), ('detroit', 'Detroit'), ('minneapolis', 'Minneapolis'),
                ('amsterdam', 'Amsterdam'), ('paris', 'Paris'), ('rome', 'Rome')])
    first_name = StringField('First name: ', validators=[validators.Length(min=1, max=30)])
    last_name = StringField('Last name: ', validators=[validators.Length(min=1, max=30)])
    address = StringField('Address', validators=[validators.Length(min=1, max=30)])
    username = StringField('Username: ', validators=[validators.Length(min=1, max=30)])
    password = PasswordField('Password: ', validators=[validators.Length(min=1, max=30)])
    submit = SubmitField('Register')
    
    