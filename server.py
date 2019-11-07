# This file contains the main web application server
from flask import Flask, __version__, render_template, session, redirect, flash, url_for, Markup
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError
from movr.movr import MovR
from web.forms import CredentialForm, RegisterForm, VehicleForm, StartRideForm, EndRideForm
from web.config import DevConfig

# Initialize the app
app = Flask(__name__)
app.config.from_object(DevConfig)
bootstrap = Bootstrap(app)
login = LoginManager(app)

# Initialize the db connection
conn_string = app.config.get('DATABASE_URI')
try:
    movr = MovR(conn_string)
except Exception as error:
    print('Error: %s' % error)
    initdb_uri = app.config.get('DEFAULT_DATABASE_URI')
    initdb = create_engine(initdb_uri)
    initdb.execute("CREATE DATABASE IF NOT EXISTS movr")
    initdb.execute("USE movr")
    movr = MovR(conn_string)

# Define user_loader function for login manager
@login.user_loader
def load_user(user_id):
    return movr.get_user(user_id=user_id)

# ROUTES
# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page():
    session['riding'] = None
    return render_template('home.html')


# Login page 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return render_template('login.html', title='Log In')
    else:
        form = CredentialForm()
        if form.validate_on_submit():
            try:
                user = movr.get_user(username=form.username.data)
                if user is None or not check_password_hash(user.password_hash, form.password.data):
                    flash(Markup('Invalid user credentials.<br>If you aren\'t registered with MovR, go <a href="%s">Sign Up</a>!') % url_for('register'))
                    return redirect(url_for('login'))
                
                login_user(user)
                return redirect(url_for('home_page'))
            except Exception as error:
                flash('Error: %s' % error)
                return redirect(url_for('login'))
        return render_template('login.html', title='Log In', form=form)


# Logout route
@login_required
@app.route('/logout')
def logout():
    logout_user()
    session['riding'] = None
    flash('You have successfully logged out.')
    return redirect('/login')


# Registration page
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return render_template('register.html', title='Sign Up')
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            try:
                movr.add_user(city=form.city.data, first_name=form.first_name.data, last_name=form.last_name.data, address=form.address.data, username=form.username.data, password=form.password.data)
                flash('Registration successful! You can now log in as %s.' % form.username.data)
                return redirect(url_for('login'))
            except DBAPIError as sql_error:
                flash('Registration failed. Make sure that you choose a unique username!')
                return redirect(url_for('register'))
            except Exception as error:
                flash('Error: %s' % error)
                return redirect(url_for('register'))
        return render_template('register.html', title='Sign Up', form=form)


# Vehicles page
@login_required
@app.route('/vehicles', methods=['GET'])
def vehicles():
    form = StartRideForm()
    vehicles = movr.get_vehicles(current_user.city)
    return render_template('vehicles.html', title='Vehicles', vehicles=vehicles, form=form) 


# Add vehicles route
@login_required
@app.route('/vehicles/add', methods=['GET','POST'])
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        try:
            movr.add_vehicle(city=form.city.data, owner_id=current_user.id, last_location=form.location.data, type=form.type.data, color=form.color.data, brand=form.brand.data, status='available')
            flash('Vehicle added!')
            return redirect(url_for('vehicles'))
        except Exception as error:
            flash('Error: %s' % error)
            return redirect(url_for('vehicles'))
    return render_template('vehicles-add.html', title='Add a vehicle', form=form)


# Rides page
@login_required
@app.route('/rides', methods=['GET'])
def rides():
    form = EndRideForm()
    rides = movr.get_rides(current_user.id)
    for ride in rides:
        if current_user.id == ride['rider_id']:
            if ride['end_time'] == None:
                session['riding'] = True
                pass
    return render_template('rides.html', title='Rides', rides=reversed(rides), form=form, riding=session['riding'])


# Start ride route
@login_required
@app.route('/rides/start/<vehicle_id>', methods=['POST'])
def start_ride(vehicle_id):
    try:
        if session['riding'] == None:
            rides = movr.get_rides(current_user.id)
            for ride in rides:
                if current_user.id == ride['rider_id']:
                    if ride['end_time'] == None:
                        session['riding'] = True
                        pass
        if session['riding']:
            flash('You are already riding. End your current ride before starting a new one!')
            return redirect(url_for('rides'))
        movr.start_ride(city=current_user.city, rider_id=current_user.id, vehicle_id=vehicle_id)
        session['riding'] = True
        flash('Ride started.')
        return redirect(url_for('rides'))
    except Exception as error:
        flash('Error: %s' % error)
        return redirect(url_for('vehicles'))
    

# End ride route
@login_required
@app.route('/rides/end/<ride_id>', methods=['POST'])
def end_ride(ride_id):
    try:
        movr.end_ride(city=current_user.city, ride_id=ride_id)
        session['riding'] = False
        flash('Ride ended.')
        return redirect(url_for('rides'))
    except Exception as error:
        flash('Error: %s' % error)
        return redirect(url_for('vehicles'))


# Users page
@login_required
@app.route('/users', methods=['GET'])
def users():
    if current_user.is_authenticated:
        users = movr.get_users(current_user.city)
        return render_template('users.html', title='Users', users=users)
    else:
        flash('You need to log in to see active users in your city!')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
