# This file contains utility functions
from flask import render_template
from requests import HTTPError
from functools import wraps
import psycopg2
from movr.callbacks import get_credentials_callback

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


def validate_creds(username, password):
    try:
        uc = get_credentials_callback(username=username)
        if password == uc.password:
            return True
        else:
            return False
    except Exception:
        return False
