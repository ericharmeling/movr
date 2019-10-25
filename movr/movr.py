from cockroachdb.sqlalchemy import run_transaction
from sqlalchemy import create_engine, cast, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import registry
registry.register("cockroachdb", "cockroachdb.sqlalchemy.dialect", "CockroachDBDialect")

from movr.models import Base, User, Vehicle, Ride, VehicleLocationHistory, PromoCode, UserPromoCode
from movr.callbacks import start_ride_callback, end_ride_callback, update_ride_location_callback, add_user_callback, add_vehicle_callback, get_users_callback, get_vehicles_callback, get_rides_callback, get_promo_codes_callback, add_promo_code_callback, apply_promo_code_callback, register_user_callback
import logging

class MovR:
    def __init__(self, conn_string, init_tables = True, echo = False):
        self.engine = create_engine(conn_string, convert_unicode=True, echo=echo)
        
        if init_tables:
            logging.info("Initializing tables")
            metadata=MetaData()
            metadata.create_all(bind=self.engine)
            logging.debug("Tables created")

        self.session = sessionmaker(bind=self.engine)()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


    def start_ride(self, city, rider_id, vehicle_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: start_ride_callback(session, city, rider_id, vehicle_id))


    def end_ride(self, city, ride_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: end_ride_callback(session, city, ride_id))


    def update_ride_location(self, city, ride_id, lat, long):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: update_ride_location_callback(session, city, ride_id, lat, long))


    def add_user(self, city, name, address, credit_card_number):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_user_callback(session, city, name, address, credit_card_number))

    def register_user(self, city, name, address, credit_card_number, username, password):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: register_user_callback(session, city, name, address, credit_card_number, username, password))

    def add_vehicle(self, city, owner_id, current_location, type, vehicle_metadata, status):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_vehicle_callback(session, city, owner_id, current_location, type, vehicle_metadata, status))


    def get_users(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_users_callback(session, city, limit))


    def get_vehicles(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_vehicles_callback(session, city, limit))


    def get_rides(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_rides_callback(session, city, limit))


    def get_promo_codes(self, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_promo_codes_callback(session, limit))


    def create_promo_code(self, code, description, expiration_time, rules):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_promo_code_callback(session, code, description, expiration_time, rules))


    def apply_promo_code(self, user_city, user_id, promo_code):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: apply_promo_code_callback(session, user_city, user_id, promo_code))

