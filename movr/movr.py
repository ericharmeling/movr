from cockroachdb.sqlalchemy import run_transaction
from sqlalchemy import create_engine, cast, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import registry
registry.register("cockroachdb", "cockroachdb.sqlalchemy.dialect", "CockroachDBDialect")

from movr.models import Base, User, Vehicle, Ride, VehicleLocationHistory, PromoCode, UserPromoCode
from movr.transactions import start_ride_txn, end_ride_txn, update_ride_location_txn, add_user_txn, add_vehicle_txn, get_users_txn, get_user_txn, get_vehicles_txn, get_rides_txn, get_promo_codes_txn, add_promo_code_txn, apply_promo_code_txn
import logging

class MovR:
    def __init__(self, conn_string, init_tables = True, echo = False):
        self.engine = create_engine(conn_string, convert_unicode=True, echo=echo)
        
        if init_tables:
            logging.info("Initializing tables")
            Base.metadata.create_all(bind=self.engine)
            logging.debug("Tables created")

        self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


    def start_ride(self, city, rider_id, vehicle_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: start_ride_txn(session, city, rider_id, vehicle_id))


    def end_ride(self, city, ride_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: end_ride_txn(session, city, ride_id))


    def update_ride_location(self, city, ride_id, lat, long):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: update_ride_location_txn(session, city, ride_id, lat, long))


    def add_user(self, city, first_name, last_name, address, username, password):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_user_txn(session, city, first_name, last_name, address, username, password))


    def add_vehicle(self, city, owner_id, current_location, type, color, brand, status):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_vehicle_txn(session, city, owner_id, current_location, type, color, brand, status))


    def get_users(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_users_txn(session, city, limit))


    def get_user(self, username=None, user_id=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_user_txn(session, username, user_id))


    def get_vehicles(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_vehicles_txn(session, city, limit))


    def get_rides(self, city, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_rides_txn(session, city, limit))


    def get_promo_codes(self, limit=None):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: get_promo_codes_txn(session, limit))


    def create_promo_code(self, code, description, expiration_time, rules):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_promo_code_txn(session, code, description, expiration_time, rules))


    def apply_promo_code(self, user_city, user_id, promo_code):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: apply_promo_code_txn(session, user_city, user_id, promo_code))

