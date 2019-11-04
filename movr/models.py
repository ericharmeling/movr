from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Index, String, DateTime, Integer, Float, ForeignKey, CheckConstraint, MetaData
from sqlalchemy.types import DECIMAL, BLOB
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    address = Column(String)
    username = Column(String, unique=True)
    password_hash = Column(String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def __repr__(self):
        return "<User(city='%s', id='%s', name='%s')>" % (self.city, self.id, self.first_name + ' ' + self.last_name)


class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, primary_key=True)
    type = Column(String)
    owner_id = Column(UUID, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    current_location = Column(String)
    color = Column(String)
    brand = Column(String)

    def __repr__(self):
        return "<Vehicle(city='%s', id='%s', type='%s', status='%s')>" % (self.city, self.id, self.type, self.status)


class Ride(Base):
    __tablename__ = 'rides'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, primary_key=True)
    vehicle_city = Column(String, CheckConstraint('vehicle_city=city'))
    rider_id = Column(UUID, ForeignKey('users.id'))
    vehicle_id = Column(UUID, ForeignKey('vehicles.id'))
    start_location = Column(String)
    end_location = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime)
    revenue = Column(DECIMAL(10,2))

    def __repr__(self):
        return "<Ride(city='%s', id='%s', rider_id='%s', vehicle_id='%s')>" % (self.city, self.id, self.rider_id, self.vehicle_id)


class VehicleLocationHistory(Base):
    __tablename__ = 'vehicle_location_histories'
    city = Column(String, primary_key=True)
    ride_id = Column(UUID, ForeignKey('rides.id'), primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, primary_key=True)
    location = Column(String)

    def __repr__(self):
        return "<VehicleLocationHistory(city='%s', ride_id='%s', timestamp='%s', lat='%s', long='%s')>" % \
               (self.city, self.ride_id, self.timestamp, self.lat, self.long)


class PromoCode(Base):
    __tablename__ = 'promo_codes'
    code = Column(String, primary_key=True)
    description = Column(String)
    creation_time = Column(DateTime, default=datetime.datetime.now)
    expiration_time = Column(DateTime)
    rules = Column(JSONB)

    def __repr__(self):
        return "<PromoCode(code='%s', description='%s', creation_time='%s', expiration_time='%s', rules='%s')>" % \
               (self.code, self.description, self.creation_time, self.expiration_time, self.rules)


class UserPromoCode(Base):
    __tablename__ = 'user_promo_codes'
    city = Column(String, primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    code = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return "<UserPromoCode(city='%s', user_id='%s', code='%s', timestamp='%s')>" % \
               (self.user_city, self.user_id, self.code, self.timestamp)

