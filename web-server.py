from flask import Flask, Response, __version__, request, jsonify, render_template, session
from scripts.movr import MovR
from index import make_conn_string
from uuid import UUID
import requests
from requests import HTTPError
import geocoder
from scripts.utils import get_region, validate_creds
import scripts.forms as forms

app = Flask(__name__)

# Hardcoded config variables for debugging
DEBUG = True

# 
if DEBUG:
    HOST = 'localhost'
    PORT = '26257'
    URL = HOST + PORT
    REGION = 'us_east'
    CITY = 'new york'
    CURRENT_LOCATION = '23rd Street, New York, New York'
    SECRET_KEY = 'secret_key'
    conn_string = 'cockroachdb://root@localhost:26257/movr'
else:
    g = geocoder.ip('me')
    CURRENT_LOCATION = g.json['address']
    CITY = g.city
    REGION = get_region(CITY)
    conn_string = make_conn_string(REGION)

# Connect to database
movr = MovR(conn_string)

# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page(username=''):
    return render_template('home.html', user=username, city=CITY)

# Login page 
# TO-DO : Implement POST endpoint function for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        try:
            if session['logged_in']:
                return render_template('login.html', login_err='You are already logged in as %s') % (session['username'],)
        except KeyError as key_error:
            pass
        try:
            if forms.CredentialForm(request.form).validate():
                username = request.form['username'].lower()
                password = request.form['password']
                if validate_creds(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return render_template('home.html', user=username)
                else:
                    return render_template('login.html', login_err='Invalid credentials! Username or password in not database.')
            else:
                    return render_template('login.html', login_err='Invalid credentials! Bad syntax.')
        except HTTPError as http_error:
            print(f'HTTP error: {http_error}\n')
        except Exception as error:
            print(f'Error: {error}\n')

# Vehicles page
@app.route('/vehicles', methods=['GET'])
def vehicles_page():
    vehicles = movr.get_vehicles(CITY)
    return render_template('vehicles.html', vehicles=vehicles, login_err='')


# Add vehicles route
@app.route('/vehicles/add', methods=['GET', 'POST'])
def vehicles():
    vehicles = movr.get_vehicles(CITY)
    if request.method == 'POST':
        if session.get('logged_in')==False or session.get('logged_in')==None:
            return render_template('vehicles.html', vehicles=vehicles, login_err='You need to log in to add vehicles!')
        else:
            try:
                r = request.form
                MovR(conn_string).add_vehicle(city=r['city'], owner_id=r['owner_id'], current_location=r['current_location'], type=r['type'], vehicle_metadata=r['vehicle_metadata'], status='available')
            except HTTPError as http_error:
                print(f'HTTP error: {http_error}\n')
            except Exception as error:
                print(f'Error: {error}\n')
    else:
        return vehicles

# Rides page
@app.route('/rides', methods=['GET'])
def rides_page():
    rides = movr.get_active_rides(CITY)
    return render_template('rides.html', rides=rides, login_err='')

# Start ride route
@app.route('/rides/start', methods=['GET', 'POST'])
def start_ride():
    if request.method == 'POST':
        r = request.form
        try:
            MovR(conn_string).start_ride(city=r['city'], rider_id=r['rider_id'], vehicle_id=r['vehicle_id'])
            render_template('vehicles.html', vehicles=vehicles, login_err='')
        except HTTPError as http_error:
            print(f'HTTP error: {http_error}\n')
        except Exception as error:
            print(f'Error: {error}\n')
    else:
        return vehicles

if __name__ == '__main__':
    app.secret_key = SECRET_KEY
    app.run(host=HOST, debug=DEBUG)
