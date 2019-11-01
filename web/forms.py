from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, validators

# Fields
class CityField(SelectField):
    label='City: '
    choices=[('new york', 'New York'), ('boston', 'Boston'), ('washington dc', 'Washington DC'),
                ('san francisco', 'San Francisco'), ('seattle', 'Seattle'), ('los angeles', 'Los Angeles'),
                ('chicago', 'Chicago'), ('detroit', 'Detroit'), ('minneapolis', 'Minneapolis'),
                ('amsterdam', 'Amsterdam'), ('paris', 'Paris'), ('rome', 'Rome')]

class UserIdField(StringField):
    label = ('User ID: ')
    validators = [validators.required(), validators.Length(min=1, max=30)]


# Forms
class CredentialForm(FlaskForm):
    username = StringField('Username: ', validators=[validators.Length(min=1, max=30)])
    password = PasswordField('Password: ', validators=[validators.Length(min=1, max=30)])
    submit = SubmitField('Sign In')

class VehicleForm(FlaskForm):
    city = CityField()
    vtype = SelectField(label='Vehicles', choices=[('bike', 'Bike'), ('scooter', 'Scooter'), ('skateboard', 'Skateboard')])
    owner = UserIdField(label='Owner ID: ')

class LocationForm(FlaskForm):
    city = CityField(label='What city are you in?')
    current_location = StringField(label='What\'s your location?')

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
    
    