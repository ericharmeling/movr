from movr.models import Vehicle, UserPromoCode, PromoCode, Ride, VehicleLocationHistory, User, UserCredentials
import datetime
import uuid
import random

def start_ride_callback(session, city, rider_id, vehicle_id):
    v = session.query(Vehicle).filter_by(city=city, id=vehicle_id).first()
    r = Ride(city=city, vehicle_city=city, id=str(uuid.uuid4()), rider_id=rider_id, vehicle_id=vehicle_id, start_address=v.current_location)
    session.add(r)
    v.status = "in_use"
    return {'city': r.city, 'id': r.id}


def end_ride_callback(session, city, ride_id):
    ride = session.query(Ride).filter_by(city=city, id=ride_id).first()
    v = session.query(Vehicle).filter_by(city=city, id=ride.vehicle_id).first()
    ride.end_address = v.current_location
    ride.revenue = random.uniform(1,100)
    ride.end_time = datetime.datetime.now()
    v.status = "available"


def update_ride_location_callback(session, city, ride_id, lat, long):
    h = VehicleLocationHistory(city = city, ride_id = ride_id, lat = lat, long = long)
    session.add(h)


def add_user_callback(session, city, name, address, credit_card_number, id=str(uuid.uuid4())):
    u = User(city=city, id=id, name=name, address=address, credit_card=credit_card_number)
    session.add(u)
    return {'city': u.city, 'id': u.id}

def add_vehicle_callback(session, city, owner_id, current_location, type, vehicle_metadata, status):
    vehicle_type = type
    vehicle = Vehicle(id=str(uuid.uuid4()), type=vehicle_type, city=city, owner_id=owner_id, current_location = current_location, status=status, ext=vehicle_metadata)
    session.add(vehicle)
    return {'city': vehicle.city, 'id': vehicle.id}


def get_users_callback(session, city, limit=None):
    users = session.query(User).filter_by(city=city).limit(limit).all()
    return list(map(lambda user: {'city': user.city, 'id': user.id, 'name': user.name}, users))


def get_vehicles_callback(session, city, limit=None):
    vehicles = session.query(Vehicle).filter_by(city=city).limit(limit).all()
    return list(map(lambda vehicle: {'city': vehicle.city, 'id': vehicle.id, 'type': vehicle.type, 'current_location': vehicle.current_location + ', ' + vehicle.city, 'status': vehicle.status, 'ext': vehicle.ext}, vehicles))


def get_rides_callback(session, city, limit=None):
    rides = session.query(Ride).filter_by(city=city).limit(limit).all()
    return list(map(lambda ride: {'city': ride.city, 'id': ride.id, 'vehicle_id': ride.vehicle_id, 'start_time': ride.start_time, 'end_time': ride.end_time}, rides))


def get_promo_codes_callback(session, limit=None):
    pcs = session.query(PromoCode).limit(limit).all()
    return list(map(lambda pc: pc.code, pcs))


def add_promo_code_callback(session, code, description, expiration_time, rules):
    pc = PromoCode(code = code, description = description, expiration_time = expiration_time, rules = rules)
    session.add(pc)
    return pc.code


def apply_promo_code_callback(session, user_city, user_id, code):
    pc = session.query(PromoCode).filter_by(code=code).one_or_none()
    if pc:
        upc = session.query(UserPromoCode).\
            filter_by(city = user_city, user_id = user_id, code = code).one_or_none()
        if not upc:
            upc = UserPromoCode(city = user_city, user_id = user_id, code = code)
            session.add(upc)

def register_user_callback(session, city, name, address, credit_card_number, username, password):
    id=str(uuid.uuid4())
    add_user_callback(session, city, name, address, credit_card_number, id=id)
    uc = UserCredentials(user_city=city, user_id=id, username=username, password=password)
    return {'username': uc.username, 'password': uc.password}

def get_credentials_callback(session, username):
    uc = session.query(UserCredentials).filter_by(username=username)
    return {'username': uc.username, 'password': uc.password}