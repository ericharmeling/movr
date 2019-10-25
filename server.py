from flask import Flask, Response, __version__, request, jsonify, render_template, session
from movr.movr import MovR
from movr.location import Location
from requests import HTTPError, get
from movr.utils import validate_creds, post_error, try_route
from config import DevConfig

app = Flask(__name__)
app.config.from_object(DevConfig)

# Connect to the database
conn_string = app.config.get('DATABASE_URI')
movr = MovR(conn_string)

# ROUTES
# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page(username=''):
    session['location'] = Location().__dict__
    print(session['location'])
    try:
        return render_template('home.html', username=session['username'], city=session['location']['city'])
    except KeyError as key_error:
        return render_template('home.html', city=session['location']['city'])


# Login page 
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
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        r = request.form
        MovR(conn_string).register_user(city=r['city'].lower(), name=r['name'], address=r['address'], credit_card_number=r['credit_card'], username=r['username'], password=r['password'])
        session['logged_in'] = True
        session['username'] = r['username']
        users = movr.get_users(session['location']['city'])
        return render_template('users.html', users=users, err='')


# Vehicles page
@app.route('/vehicles', methods=['GET'])
def vehicles_page():
    vehicles = movr.get_vehicles(session['location']['city'])
    return render_template('vehicles.html', vehicles=vehicles, err='')


# Add vehicles route
@app.route('/vehicles/add', methods=['GET','POST'])
def vehicles():
    if request.method == 'GET':
        return render_template('vehicles-add.html')
    else:
        try:
            if session['logged_in']:
                @try_route
                def post_try():
                    r = request.form
                    ext = { k: v for k, v in {'Brand':r['brand'], 'Color':r['color']}.items() if v not in (None,'')}
                    MovR(conn_string).add_vehicle(city=r['city'].lower(), owner_id=r['owner_id'], current_location=r['current_location'], type=r['type'], vehicle_metadata=ext, status='available')
                    vehicles = movr.get_vehicles(session['location']['city'])
                    return render_template('vehicles.html', vehicles=vehicles)
                return post_try()
            else:
                vehicles = movr.get_vehicles(session['location']['city'])
                return render_template('vehicles.html', vehicles=vehicles, err='You need to log in to add vehicles!')
        except KeyError as key_error:
            vehicles = movr.get_vehicles(session['location']['city'])
            return render_template('vehicles.html', vehicles=vehicles, err='You need to log in to add vehicles!')


# Rides page
@app.route('/rides', methods=['GET'])
def rides_page():
    rides = movr.get_rides(session['location']['city'])
    return render_template('rides.html', rides=reversed(rides))


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
                rides = movr.get_rides(session['location']['city'])
                return render_template('rides.html', rides=reversed(rides))
            return post_try()
        else:
            @try_route
            def error_page():
                vehicles = movr.get_vehicles(session['location']['city'])
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
@app.route('/users', methods=['GET'])
def users_page():
    users = movr.get_users(session['location']['city'])
    return render_template('users.html', users=users, err='', logged_in=session['logged_in'])


if __name__ == '__main__':
    app.run()
