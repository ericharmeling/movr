from movr.models import Vehicle, Ride, User
from sqlalchemy import cast, Numeric
import datetime
import uuid
import decimal

def start_ride_txn(session, city, rider_id, vehicle_id):
    v = session.query(Vehicle).filter_by(city=city, id=vehicle_id).first()
    r = Ride(city=city, id=str(uuid.uuid4()), rider_id=rider_id, vehicle_id=vehicle_id, start_location=v.last_location)
    session.add(r)
    v.status = "unavailable"


def end_ride_txn(session, city, ride_id, location):
    r = session.query(Ride).filter_by(city=city, id=ride_id).first()
    v = session.query(Vehicle).filter_by(city=city, id=r.vehicle_id).first()
    r.end_location = location
    r.end_time = datetime.datetime.now()
    r.length = r.end_time - r.start_time
    r.revenue = 1 + cast(r.length, Numeric)*.02
    v.last_location = location
    v.status = "available"


def add_user_txn(session, city, first_name, last_name, email, username, password, password_hash=None, is_owner=False):
    u = User(city=city, id=str(uuid.uuid4()), first_name=first_name, last_name=last_name, email=email, username=username, is_owner=is_owner)
    u.set_password(password)
    session.add(u)


def remove_user_txn(session, city, id):
    u = session.query(User).filter_by(city=city, id=id).first()
    u.username = None


def add_vehicle_txn(session, city, owner_id, last_location, type, color, brand, status, is_owner):
    vehicle_type = type
    v = Vehicle(id=str(uuid.uuid4()), type=vehicle_type, city=city, owner_id=owner_id, last_location = last_location, color=color, brand=brand, status=status)
    session.add(v)
    if not is_owner:
        u = session.query(User).filter_by(id=v.owner_id).first()
        u.is_owner = True


def remove_vehicle_txn(session, city, id):
    v = session.query(Vehicle).filter_by(city=city, id=id).first()
    owner = v.owner_id
    session.delete(v)
    vehicles = session.query(Vehicle).filter_by(city=city, owner_id=owner).all()
    if not vehicles:
        u = session.query(User).filter_by(city=city, id=owner).first()
        u.is_owner = False


def get_users_txn(session, city):
    users = session.query(User).filter_by(city=city).all()
    return list(map(lambda user: {'city': user.city, 'id': user.id, 'name': user.username, 'first_name': user.first_name, 'last_name': user.last_name, 'is_owner': user.is_owner}, users))


def get_user_txn(session, username=None, user_id=None):
    if username:
        u = session.query(User).filter_by(username=username).first()
    elif user_id:
        u = session.query(User).filter_by(id=user_id).first()
    if u:
        session.expunge(u)
    return u


def get_vehicles_txn(session, city):
    vehicles = session.query(Vehicle).filter_by(city=city).all()
    return list(map(lambda vehicle: {'city': vehicle.city, 'id': vehicle.id, 'owner_id': vehicle.owner_id, 'type': vehicle.type, 'last_location': vehicle.last_location + ', ' + vehicle.city, 'status': vehicle.status, 'date_added': vehicle.date_added, 'color': vehicle.color, 'brand': vehicle.brand}, vehicles))


def get_rides_txn(session, city, rider_id):
    rides = session.query(Ride).filter_by(city=city, rider_id=rider_id).order_by(Ride.start_time).all()
    return list(map(lambda ride: {'city': ride.city, 'id': ride.id, 'vehicle_id': ride.vehicle_id, 'start_time': ride.start_time, 'end_time': ride.end_time, 'rider_id': ride.rider_id, 'length': ride.length, 'revenue': ride.revenue}, rides))

