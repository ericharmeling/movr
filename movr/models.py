
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Index, String, DateTime, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import datetime

#@todo: add interleaving
#@todo: restore FKs and "relationship' functionality after this is fixed: https://github.com/cockroachdb/cockroach/issues/36859

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, primary_key=True)
    name = Column(String)
    address = Column(String)
    credit_card = Column(String)

    def __repr__(self):
        return "<User(city='%s', id='%s', name='%s')>" % (self.city, self.id, self.name)

#@todo: sqlalchemy fails silently if compound fks are in the wrong order.
class Ride(Base):
    __tablename__ = 'rides'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, ForeignKey('users.city'), primary_key=True) #FK requires an index or it fails silently:  https://github.com/cockroachdb/cockroach/issues/22253
    vehicle_city = Column(String, CheckConstraint('vehicle_city=city'), ForeignKey('vehicles.city')) #@todo: annoying workaround for https://github.com/cockroachdb/cockroach/issues/23580
    rider_id = Column(UUID, ForeignKey('users.id'))
    vehicle_id = Column(UUID, ForeignKey('vehicles.id'))
    start_address = Column(String)
    end_address = Column(String)
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime)
    revenue = Column(DECIMAL(10,2))

    def __repr__(self):
        return "<Ride(city='%s', id='%s', rider_id='%s', vehicle_id='%s')>" % (self.city, self.id, self.rider_id, self.vehicle_id)

class VehicleLocationHistory(Base):
    __tablename__ = 'vehicle_location_histories'
    city = Column(String, ForeignKey('rides.city'), primary_key=True)
    ride_id = Column(UUID, ForeignKey('rides.id'), primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now, primary_key=True)
    lat = Column(Float)
    long = Column(Float)

    def __repr__(self):
        return "<VehicleLocationHistory(city='%s', ride_id='%s', timestamp='%s', lat='%s', long='%s')>" % \
               (self.city, self.ride_id, self.timestamp, self.lat, self.long)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(UUID, default=str(uuid.uuid4()), primary_key=True)
    city = Column(String, ForeignKey('users.city'), primary_key=True)
    type = Column(String)
    owner_id = Column(UUID, ForeignKey('users.id'))
    creation_time = Column(DateTime, default=datetime.datetime.now)
    status = Column(String)
    current_location = Column(String)
    ext = Column(JSONB)

    def __repr__(self):
        return "<Vehicle(city='%s', id='%s', type='%s', status='%s', ext='%s')>" % (self.city, self.id, self.type, self.status, self.ext)

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
    city = Column(String, ForeignKey('users.city'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.user_id'), primary_key=True)
    code = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return "<UserPromoCode(city='%s', user_id='%s', code='%s', timestamp='%s')>" % \
               (self.user_city, self.user_id, self.code, self.timestamp)

class UserCredentials(Base):
    __tablename__ = 'user_credentials'
    user_city = Column(String, ForeignKey('users.city'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)

    def __repr__(self):
        return "<UserCredentials(city='%s', user_id='%s', username='%s', password='%s')>" % \
               (self.user_city, self.user_id, self.username, self.password)
