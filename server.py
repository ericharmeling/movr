from flask import Flask, __version__, request, render_template, session, redirect, flash, url_for, Markup
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from movr.movr import MovR
from web.forms import CredentialForm, RegisterForm, VehicleForm
from web.utils import validate_creds, render_or_error, try_route, get_region
from web.config import DevConfig
from requests import HTTPError

# Initialize the app
app = Flask(__name__)
app.config.from_object(DevConfig)
bootstrap = Bootstrap(app)
login = LoginManager(app)
conn_string = app.config.get('DATABASE_URI')
movr = MovR(conn_string)
@login.user_loader
def load_user(user_id):
    return movr.get_user(user_id=user_id)

# ROUTES
# Home page
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home_page():
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
                user = movr.get_user(form.username.data)
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
            if not get_region(form.city.data):
                flash('Unfortunately, MovR hasn\'t made it to your city yet. Try coming back later!')
                return redirect(url_for('home_page'))
            try:
                movr.add_user(city=form.city.data, first_name=form.first_name.data, last_name=form.last_name.data, address=form.address.data, username=form.username.data, password=form.password.data)
                flash('Registration successful! You can now log in as %s.' % form.username.data)
                return redirect(url_for('login'))
            except Exception as error:
                flash('Error: %s' % error)
                return redirect(url_for('register'))
        return render_template('register.html', title='Sign Up', form=form)


# Vehicles page
@login_required
@app.route('/vehicles', methods=['GET'])
def vehicles():
    vehicles = movr.get_vehicles(current_user.city)
    return render_template('vehicles.html', title='Vehicles', vehicles=vehicles)


# Add vehicles route
@login_required
@app.route('/vehicles/add', methods=['GET','POST'])
def add_vehicle():
    form = VehicleForm()
    if form.validate_on_submit():
        try:
            movr.add_vehicle(city=form.city.data, owner_id=current_user.id, current_location=form.location.data, type=form.type.data, color=form.color.data, brand=form.brand.data, status='available')
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
    rides = movr.get_rides(session['location']['city'])
    return render_template('rides.html', rides=reversed(rides))


# Start ride route
@login_required
@app.route('/rides/start', methods=['POST'])
def start_ride():
    r = request.form
    try:
        if session['logged_in']:
            @try_route
            def post_try():
                movr.start_ride(city=r['city'], rider_id=r['rider_id'], vehicle_id=r['vehicle_id'])
                session['riding'] = True
                rides = movr.get_rides(current_user.city)
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
@login_required
@app.route('/rides/end', methods=['POST'])
def end_ride():
    r = request.form
    @try_route
    def post_try():
        movr.end_ride(city=r['city'], vehicle_id=r['vehicle_id'])
        return render_template('vehicles.html', vehicles=vehicles, err='')
    return post_try()


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
