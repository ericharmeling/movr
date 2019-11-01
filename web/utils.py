# This file contains utility functions for the MovR Flask app
from flask import render_template
from requests import HTTPError
from functools import wraps
import psycopg2
from movr.transactions import get_user_txn

# Post error message
def render_or_error(page='home.html', err_message='An error occurred!', *args, **kwds):
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
            return render_or_error(err_message=message)
        except psycopg2.Error as sql_error:
            message = f'SQL Error: {sql_error}\n'
            print(message)
            return render_or_error(err_message=message)
        except Exception as error:
            message = f'Error: {error}\n'
            print(message)
            return render_or_error(err_message=message)
    return wrapper


def validate_creds(username, password):
    try:
        uc = get_user_txn(username=username)
        if password == uc.password:
            return True
        else:
            return False
    except Exception:
        return False


def get_region(city):
    city = city.lower()
    if city in ('new york', 'boston', 'washington dc'):
        return 'us_east'
    elif city in ('san francisco', 'seattle', 'los angeles'):
        return 'us_west'
    elif city in ('chicago', 'detroit', 'minneapolis'):
        return 'us-mid'
    elif city in ('amsterdam', 'paris', 'rome'):
        return 'europe'
    else:
        return 'unknown'
