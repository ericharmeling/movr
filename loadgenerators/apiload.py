#!/usr/bin/python

import argparse
import datetime
import logging
import math
import os
import random
import re
import signal
import sys
import threading
import time
import requests

sys.path.append(os.path.abspath('../'))
from scripts.generators import MovRGenerator

from faker import Faker

from scripts.movr import MovR
from scripts.movr_stats import MovRStats
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode

from cockroachdb.sqlalchemy import run_transaction
from scripts.models import User, Vehicle, Ride, VehicleLocationHistory, PromoCode

RUNNING_THREADS = []
TERMINATE_GRACEFULLY = False
DEFAULT_READ_PERCENTAGE = .95

ACTION_ADD_VEHICLE = "add vehicle"
ACTION_GET_VEHICLES = "get vehicles"
ACTION_UPDATE_RIDE_LOC = "log ride location"
ACTION_NEW_CODE = "new promo code"
ACTION_APPLY_CODE = "apply promo code"
ACTION_NEW_USER = "new user"
ACTION_START_RIDE = "start ride"
ACTION_END_RIDE = "end ride"

def signal_handler(sig, frame):
    global TERMINATE_GRACEFULLY
    grace_period = 15
    logging.info('Waiting at most %d seconds for threads to shutdown...', grace_period)
    TERMINATE_GRACEFULLY = True

    start = time.time()
    while threading.active_count() > 1:
        if (time.time() - start) > grace_period:
            logging.info("grace period has passed. killing threads.")
            os._exit(1)
        else:
            time.sleep(.1)

    logging.info("shutting down gracefully.")
    sys.exit(0)


DEFAULT_PARTITION_MAP = {
    "us_east": ["new york", "boston", "washington dc"],
    "us_west": ["san francisco", "seattle", "los angeles"],
    "us_central": ["chicago", "detroit", "minneapolis"],
    "eu_west": ["amsterdam", "paris", "rome"]
}



# Generates evenly distributed load among the provided cities


def simulate_movr_load(api_url, cities):


    while True:

        if TERMINATE_GRACEFULLY:
            logging.debug("Terminating thread.")
            return

        active_city = random.choice(cities)

        start = time.time()
        r = requests.get(api_url)
        stats.add_latency_measurement("get vehicles", time.time() - start)


# creates a map of partions when given a list of pairs in the form <partition>:<city_id>.
def extract_region_city_pairs_from_cli(pair_list):
    if pair_list is None:
        return DEFAULT_PARTITION_MAP

    city_pairs = {}

    for city_pair in pair_list:
        pair = city_pair.split(":")
        if len(pair) < 1:
            pair = ["default"].append(pair[0])
        else:
            pair = [pair[0], ":".join(pair[1:])]  # if there are many semicolons convert this to only two items


        city_pairs.setdefault(pair[0],[]).append(pair[1])

    return city_pairs

def get_cities(city_list):
    cities = []
    if city_list is None:
        for partition in DEFAULT_PARTITION_MAP:
            cities += DEFAULT_PARTITION_MAP[partition]
        return cities
    else:
        return city_list

def extract_zone_pairs_from_cli(pair_list):
    if pair_list is None:
        return {}

    zone_pairs = {}

    for zone_pair in pair_list:
        pair = zone_pair.split(":")
        if len(pair) < 1:
            pair = ["default"].append(pair[0])
        else:
            pair = [pair[0], ":".join(pair[1:])]  # if there are many colons convert this to only two items

        zone_pairs.setdefault(pair[0], "")
        zone_pairs[pair[0]] = pair[1]

    return zone_pairs

def set_query_parameter(url, param_name, param_value):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

def setup_parser():
    parser = argparse.ArgumentParser(description='CLI for MovR.')
    subparsers = parser.add_subparsers(dest='subparser_name')

    ###########
    # GENERAL COMMANDS
    ##########
    parser.add_argument('--num-threads', dest='num_threads', type=int, default=5,
                            help='The number threads to use for MovR (default =5)')
    parser.add_argument('--log-level', dest='log_level', default='info',
                        help='The log level ([debug|info|warning|error]) for MovR messages. (default = info)')
    parser.add_argument('--url', dest='conn_string',
                        help="connection string to movr database. Default is 'postgres://root@localhost:26257/movr?sslmode=disable'")


    ###############
    # RUN COMMANDS
    ###############
    run_parser = subparsers.add_parser('run', help="generate fake traffic for the movr database")

    run_parser.add_argument('--city', dest='city', action='append',
                            help='The names of the cities to use when generating load. Use this flag multiple times to add multiple cities.')
    run_parser.add_argument('--read-only-percentage', dest='read_percentage', type=float,
                            help='Value between 0-1 indicating how many simulated read-only home screen loads to perform as a percentage of overall activities',
                            default=.95)

    return parser



# generate fake load for objects within the provided city list
def run_load_generator(conn_string, read_percentage, city_list, num_threads):
    if read_percentage < 0 or read_percentage > 1:
        raise ValueError("read percentage must be between 0 and 1")


    logging.info("simulating movr load for cities %s", city_list)


    RUNNING_THREADS = []
    for i in range(num_threads):
        t = threading.Thread(target=simulate_movr_load, args=(conn_string, city_list ))
        t.start()
        RUNNING_THREADS.append(t)

    while True: #keep main thread alive to catch exit signals
        time.sleep(15)

        stats.print_stats(action_list=[ACTION_ADD_VEHICLE, ACTION_GET_VEHICLES, ACTION_UPDATE_RIDE_LOC,
                           ACTION_NEW_CODE, ACTION_APPLY_CODE, ACTION_NEW_USER,
                           ACTION_START_RIDE, ACTION_END_RIDE])

        stats.new_window()


if __name__ == '__main__':

    global stats
    stats = MovRStats()
    # support ctrl + c for exiting multithreaded operation
    signal.signal(signal.SIGINT, signal_handler)

    args = setup_parser().parse_args()

    if args.num_threads <= 0:
        logging.error("Number of threads must be greater than 0.")
        sys.exit(1)

    if args.log_level not in ['debug', 'info', 'warning', 'error']:
        logging.error("Invalid log level: %s", args.log_level)
        sys.exit(1)

    level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR
    }

    logging.basicConfig(level=level_map[args.log_level],
                        format='[%(levelname)s] (%(threadName)-10s) %(message)s', )


    #format connection string to work with our cockroachdb driver.
    conn_string = args.conn_string
    print(conn_string)


    run_load_generator(conn_string, .95, ["new york"], args.num_threads)








