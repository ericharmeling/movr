from flask import Flask, Response, __version__, request, jsonify, render_template, session
from scripts.movr import MovR
from index import make_conn_string
from uuid import UUID
import requests
from requests import HTTPError
import geocoder
from scripts.utils import get_region, validate_creds, post_error, try_route
import scripts.forms as forms
from config import *

app = Flask(__name__)
app.config.from_object(DevConfig)

# Set vars
conn_string = app.config.get('DATABASE_URI')
if app.config.get('DEBUG'):
    REGION = 'us_east'
    CITY = 'new york'
    CURRENT_LOCATION = '23rd Street, New York, New York'
else:
    g = geocoder.ip('me')
    CURRENT_LOCATION = g.json['address']
    CITY = g.city
    REGION = get_region(CITY)

# Connect to database
movr = MovR(conn_string)


# ROUTES
# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page(username=''):
    try:
        return render_template('home.html', username=session['username'], city=CITY)
    except KeyError as key_error:
        return render_template('home.html', city=CITY)

# Login page 
# TO-DO : Implement validate_creds()
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        try:
            return render_template('login.html', logged_in=session['logged_in'], username=session['username'])
        except KeyError as key_error:
            return render_template('login.html')
    else:
        try:
            if session['logged_in']:
                return render_template('login.html', logged_in=session['logged_in'], username=session['username'])
        except KeyError as key_error:
            pass
        @try_route
        def post_try():
            username = request.form['username'].lower()
            password = request.form['password']
            if validate_creds(username, password):
                session['logged_in'] = True
                session['username'] = username
                return render_template('login.html', logged_in=session['logged_in'], username=session['username'])
            else:
                return post_error('login.html', 'Invalid credentials! Username or password not in database. Make sure you are registered with MovR.')
        return post_try()

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session['logged_in'] = False
    session['username'] = ''
    return render_template('login.html', logged_in=session['logged_in'])

# Registration page
# TO-DO : Add geolocation support
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        r = request.form
        MovR(conn_string).add_user(city=r['city'], name=r['name'], address=r['address'], credit_card_number=r['credit_card'])
        return render_template('register.html')

# Vehicles page
@app.route('/vehicles', methods=['GET'])
def vehicles_page():
    vehicles = movr.get_vehicles(CITY)
    return render_template('vehicles.html', vehicles=vehicles, err='')


# Add vehicles route
# TO-DO : Create custom fields for metadata entry
# TO-DO : Add geolocation support
@app.route('/vehicles/add', methods=['POST'])
def vehicles():
    try:
        if session['logged_in']:
            @try_route
            def post_try():
                r = request.form
                ext = { k: v for k, v in {'Brand':r['brand'], 'Color':r['color']}.items() if v not in (None,'')}
                MovR(conn_string).add_vehicle(city=r['city'], owner_id=r['owner_id'], current_location=r['current_location'], type=r['type'], vehicle_metadata=ext, status='available')
                vehicles = movr.get_vehicles(CITY)
                return render_template('vehicles.html', vehicles=vehicles)
            return post_try()
        else:
            vehicles = movr.get_vehicles(CITY)
            return render_template('vehicles.html', vehicles=vehicles, err='You need to log in to add vehicles!')
    except KeyError as key_error:
        vehicles = movr.get_vehicles(CITY)
        return render_template('vehicles.html', vehicles=vehicles, err='You need to log in to add vehicles!')

# Rides page
# TO DO: This should be visible to administrators only... You need to implement some kind of 'account type'.
@app.route('/rides', methods=['GET'])
def rides_page():
    rides = movr.get_active_rides(CITY)
    return render_template('rides.html', rides=rides)


# Start ride route
@app.route('/rides/start', methods=['POST'])
def start_ride():
    r = request.form
    try:
        if session['logged_in']:
            @try_route
            def post_try():
                MovR(conn_string).start_ride(city=r['city'], rider_id=r['rider_id'], vehicle_id=r['vehicle_id'])
                session['riding'] = True
                rides = movr.get_active_rides(CITY)
                return render_template('rides.html', rides=rides)
            return post_try()
        else:
            @try_route
            def error_page():
                vehicles = movr.get_vehicles(CITY)
                return render_template('vehicles.html', vehicles=vehicles, err='You need to log in start a ride!')
            return error_page()
    except KeyError as key_error:
        return error_page()
    

# End ride route
@app.route('/rides/end', methods=['POST'])
def end_ride():
    r = request.form
    @try_route
    def post_try():
        MovR(conn_string).end_ride(city=r['city'], vehicle_id=r['vehicle_id'])
        return render_template('vehicles.html', vehicles=vehicles, err='')
    return post_try()
# Users page
# TO DO: This should be visible to administrators only... You need to implement some kind of 'account type'.
@app.route('/users', methods=['GET'])
def users_page():
    users = movr.get_users(CITY)
    return render_template('users.html', users=users, err='')

if __name__ == '__main__':
    app.run()
