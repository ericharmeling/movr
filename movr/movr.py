from cockroachdb.sqlalchemy import run_transaction
from sqlalchemy import create_engine, cast
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.postgresql import UUID, JSONB
registry.register("cockroachdb", "cockroachdb.sqlalchemy.dialect", "CockroachDBDialect")

from movr.models import Base, User, Vehicle, Ride, VehicleLocationHistory, PromoCode, UserPromoCode
from movr.callbacks import start_ride_callback, end_ride_callback, update_ride_location_callback, add_user_callback, add_vehicle_callback, get_users_callback, get_vehicles_callback, get_rides_callback, get_promo_codes_callback, add_promo_code_callback, apply_promo_code_callback
import logging

class MovR:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def __init__(self, conn_string, init_tables = False, echo = False):
        self.engine = create_engine(conn_string, convert_unicode=True, echo=echo)

        if init_tables:
            logging.info("initializing tables")
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            logging.debug("tables dropped and created")

        self.session = sessionmaker(bind=self.engine)()


    def start_ride(self, city, rider_id, vehicle_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: start_ride_callback(session, city, rider_id, vehicle_id))


    def end_ride(self, city, ride_id):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: end_ride_callback(session, city, ride_id))


    def update_ride_location(self, city, ride_id, lat, long):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: update_ride_location_callback(session, city, ride_id, lat, long))


    def add_user(self, city, name, address, credit_card_number):
        return run_transaction(sessionmaker(bind=self.engine), lambda session: add_user_callback(session, city, name, address, credit_card_number))


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



    ############
    # GEO PARTITIONING
    ############

    def get_geo_partitioning_queries(self, partition_map, zone_map):


        def get_index_partition_name(region, index_name):
            return region + "_" + index_name

        def create_partition_string(index_name=""):
            partition_string = ""
            first_region = True
            for region in partition_map:
                region_name = get_index_partition_name(region, index_name) if index_name else region
                partition_string += "PARTITION " + region_name + " VALUES IN (" if first_region \
                    else ", PARTITION " + region_name + " VALUES IN ("
                first_region = False
                first_city = True
                for city in partition_map[region]:
                    partition_string += "'" + city + "' " if first_city else ", '" + city + "'"
                    first_city = False
                partition_string += ")"
            return partition_string

        queries_to_run = {}

        partition_string = create_partition_string()
        for table in ["vehicles", "users", "rides", "vehicle_location_histories", "user_promo_codes"]:
            partition_sql = "ALTER TABLE " + table + " PARTITION BY LIST (city) (" + partition_string + ");"
            queries_to_run.setdefault("table_partitions",[]).append(partition_sql)

            for partition_name in partition_map:
                if not partition_name in zone_map:
                    logging.info("partition_name %s not found in zone map. Skipping", partition_name)
                    continue

                zone_sql = "ALTER PARTITION " + partition_name + " OF TABLE " + table + " CONFIGURE ZONE USING constraints='[+region=" + \
                           zone_map[partition_name] + "]';"
                queries_to_run.setdefault("table_zones",[]).append(zone_sql)

        for index in [{"index_name": "rides_auto_index_fk_city_ref_users", "prefix_name": "city", "table": "rides"},
                      {"index_name": "rides_auto_index_fk_vehicle_city_ref_vehicles", "prefix_name": "vehicle_city",
                       "table": "rides"},
                      {"index_name": "vehicles_auto_index_fk_city_ref_users", "prefix_name": "city",
                       "table": "vehicles"}]:
            partition_string = create_partition_string(index_name=index["index_name"])
            partition_sql = "ALTER INDEX " + index["index_name"] + " PARTITION BY LIST (" + index[
                "prefix_name"] + ") (" + partition_string + ");"
            queries_to_run.setdefault("index_partitions",[]).append(partition_sql)

            for partition_name in partition_map:
                if not partition_name in zone_map:
                    logging.info("partition_name %s not found in zone map. Skipping", partition_name)
                    continue
                zone_sql = "ALTER PARTITION " + get_index_partition_name(partition_name,
                                                                         index["index_name"]) + " OF TABLE " + \
                           index["table"] + " CONFIGURE ZONE USING constraints='[+region=" + zone_map[
                               partition_name] + "]';"
                queries_to_run.setdefault("index_zones",[]).append(zone_sql)


        # create an index in each region so we can use the zone-config aware CBO
        for partition_name in partition_map:
            if not partition_name in zone_map:
                logging.info("partition_name %s not found in zone map. Skipping index creation for promo codes",
                             partition_name)
                continue

            sql = "CREATE INDEX promo_codes_" + partition_name + "_idx on promo_codes (code) STORING (description, creation_time, expiration_time, rules);"
            queries_to_run.setdefault("promo_code_indices",[]).append(sql)

            sql = "ALTER INDEX promo_codes@promo_codes_" + partition_name + "_idx CONFIGURE ZONE USING constraints='[+region=" + \
                  zone_map[partition_name] + "]';";
            queries_to_run.setdefault("promo_code_zones",[]).append(sql)

        return queries_to_run


    # setup geo-partitioning if this is an enterprise cluster
    def add_geo_partitioning(self, partition_map, zone_map):
        queries = self.get_geo_partitioning_queries(partition_map, zone_map)

        def add_geo_partitioning_helper(session, queries):
            for query in queries:
                session.execute(query)

        logging.info("partitioned tables...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["table_partitions"]))

        logging.info("partitioned indices...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["index_partitions"]))

        logging.info("applying table zone configs...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["table_zones"]))

        logging.info("applying index zone configs...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["index_zones"]))

        logging.info("adding indexes for promo code reference tables...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["promo_code_indices"]))

        logging.info("applying zone configs for reference table indices...")
        run_transaction(sessionmaker(bind=self.engine),
                        lambda session: add_geo_partitioning_helper(session, queries["promo_code_zones"]))









