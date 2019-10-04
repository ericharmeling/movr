# This file contains utility functions
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from requests import HTTPError
from functools import wraps
import psycopg2


# City-region matcher
us_east = ('new_york', 'boston', 'washington_dc')
us_west = ('san_francisco', 'seattle', 'los_angeles')
us_mid = ('chicago', 'detroit', 'minneapolis')
europe = ('amsterdam', 'paris', 'rome')

def get_region(city):
    if city in us_east:
        return 'us_east'
    elif city in us_west:
        return 'us_west'
    elif city in us_mid:
        return 'us-mid'
    else:
        return 'europe'


# Credential validater
# TO DO: Actually make a credential validater
def validate_creds(username, password):
    return True


# Post error message
def post_error(page='home.html', err_message='An error occurred!', *args, **kwds):
    try:
        return render_template(page, err=err_message, *args, **kwds)
    except HTTPError as http_error:
        print(f'HTTP error: {http_error}\n')
    except Exception as error:
        print(f'Error: {error}\n')


# Route exception handler decorator
def try_route(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds)
        except HTTPError as http_error:
            message = f'HTTP error: {http_error}\n'
            print(message)
            return post_error(err_message=message)
        except psycopg2.Error as sql_error:
            message = f'SQL Error: {sql_error}\n'
            print(message)
            return post_error(err_message=message)
        except Exception as error:
            message = f'Error: {error}\n'
            print(message)
            return post_error(err_message=message)
    return wrapper
