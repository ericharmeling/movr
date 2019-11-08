from movr.models import Vehicle, PromoCode, Ride, User
from sqlalchemy import cast, Numeric
import datetime
import uuid
import random
import decimal

def start_ride_txn(session, city, rider_id, vehicle_id):
    v = session.query(Vehicle).filter_by(city=city, id=vehicle_id).first()
    r = Ride(city=city, id=str(uuid.uuid4()), rider_id=rider_id, vehicle_id=vehicle_id, start_location=v.last_location)
    session.add(r)
    v.status = "unavailable"
    return {'city': r.city, 'id': r.id}


def end_ride_txn(session, city, ride_id, location, promo_code):
    ride = session.query(Ride).filter_by(city=city, id=ride_id).first()
    v = session.query(Vehicle).filter_by(city=city, id=ride.vehicle_id).first()
    ride.end_location = location
    ride.end_time = datetime.datetime.now()
    if ride.start_time and ride.end_time:
        ride.length = ride.end_time - ride.start_time
    else:
        ride.length = None
    if ride.length:
        ride.revenue = 1 + cast(ride.length, Numeric)*.02
        if promo_code: 
            promo = session.query(PromoCode).filter_by(code=promo_code).first()
            if promo:
                user = session.query(User).filter_by(id=ride.rider_id).first()
                if promo_code in user.promos_used:
                    return 'Promo already used.'
                else:
                    user.promos_used.append(promo_code)
                    ride.revenue*decimal.Decimal(.01)*promo.percent_off
            else:
                return 'Promo does not exist. Try again.'
    else:
        ride.revenue = None
    v.last_location = location
    v.status = "available"


def add_user_txn(session, city, first_name, last_name, email, username, password, password_hash=None, id=str(uuid.uuid4()), promos_used=[]):
    u = User(city=city, id=id, first_name=first_name, last_name=last_name, email=email, username=username, promos_used=promos_used)
    u.set_password(password)
    session.add(u)
    return {'city': u.city, 'id': u.id}

def add_vehicle_txn(session, city, owner_id, last_location, type, color, brand, status):
    vehicle_type = type
    vehicle = Vehicle(id=str(uuid.uuid4()), type=vehicle_type, city=city, owner_id=owner_id, last_location = last_location, color=color, brand=brand, status=status)
    session.add(vehicle)
    return {'city': vehicle.city, 'id': vehicle.id}


def get_users_txn(session, city):
    users = session.query(User).filter_by(city=city).all()
    return list(map(lambda user: {'city': user.city, 'id': user.id, 'name': user.username, 'first_name': user.first_name, 'last_name': user.last_name}, users))


def get_user_txn(session, username=None, user_id=None):
    if username:
        user = session.query(User).filter_by(username=username).first()
    elif user_id:
        user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.expunge(user)
    return user


def get_vehicles_txn(session, city):
    vehicles = session.query(Vehicle).filter_by(city=city).all()
    return list(map(lambda vehicle: {'city': vehicle.city, 'id': vehicle.id, 'type': vehicle.type, 'last_location': vehicle.last_location + ', ' + vehicle.city, 'status': vehicle.status, 'date_added': vehicle.date_added, 'color': vehicle.color, 'brand': vehicle.brand}, vehicles))


def get_rides_txn(session, rider_id):
    rides = session.query(Ride).filter_by(rider_id=rider_id).order_by(Ride.start_time).all()
    return list(map(lambda ride: {'city': ride.city, 'id': ride.id, 'vehicle_id': ride.vehicle_id, 'start_time': ride.start_time, 'end_time': ride.end_time, 'rider_id': ride.rider_id, 'length': ride.length, 'revenue': ride.revenue}, rides))


def get_promo_codes_txn(session):
    pcs = session.query(PromoCode).all()
    return list(map(lambda pc: pc.code, pcs))


def add_promo_code_txn(session, code, description, expiration_time, percent_off):
    pc = PromoCode(code = code, description = description, expiration_time = expiration_time, percent_off=percent_off) 
    session.add(pc)
    return pc.code


def apply_promo_code_txn(session, city, ride_id, user_id, code):
    pc = session.query(PromoCode).filter_by(code=code).first()
    if pc:
        user = session.query(User).filter_by(city=city, user_id=user_id).first()
        if pc.code not in user.promos_used:
            ride = session.query(Ride).filter_by(city=city, ride_id=ride_id).first()
            ride.revenue = ride.revenue*.01*pc.percent_off
            user.promos_used.append(code)
        else:
            return None
    else:
        return pc
