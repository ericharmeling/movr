from wtforms import Form, StringField, SelectField, validators

# Fields
class CityField(SelectField):
    label='City:'
    choices=[('new_york', 'New York'), ('boston', 'Boston'), ('washington_dc', 'Washington DC'),
                ('san_francisco', 'San Francisco'), ('seattle', 'Seattle'), ('los_angeles', 'Los Angeles'),
                ('chicago', 'Chicago'), ('detroit', 'Detroit'), ('minneapolis', 'Minneapolis'),
                ('amsterdam', 'Amsterdam'), ('paris', 'Paris'), ('rome', 'Rome')]

class UserIdField(StringField):
    label = ('User ID: ')
    validators = [validators.required(), validators.Length(min=1, max=30)]


# Forms
class CredentialForm(Form):
    username = StringField('Username: ', validators=[validators.required(), validators.Length(min=1, max=30)])
    password = StringField('Password: ', validators=[validators.required(), validators.Length(min=1, max=30)])

class VehicleForm(Form):
    city = CityField()
    vtype = SelectField(label='Vehicles', choices=[('bike', 'Bike'), ('scooter', 'Scooter'), ('skateboard', 'Skateboard')])
    owner = UserIdField(label='Owner ID: ')
    
    