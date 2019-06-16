from flask import Flask, Response, __version__
from flask import request
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode
import json
import os, sys
from scripts.movr import MovR




app = Flask(__name__)
source = 'https://github.com/zeit/now-examples/tree/master/python-flask'
css = '<link rel="stylesheet" href="/css/style.css" />'

#@todo: create region map
connection_string_map = {
    "iad1": os.environ["IAD_MOVR_DATABASE_URL"],
    "dub1": os.environ["DUB_MOVR_DATABASE_URL"],
    "sfo1": os.environ["SFO_MOVR_DATABASE_URL"]
}

def set_query_parameter(url, param_name, param_value):
    scheme, netloc, path, query_string, fragment = urlsplit(url)
    query_params = parse_qs(query_string)
    query_params[param_name] = [param_value]
    new_query_string = urlencode(query_params, doseq=True)
    return urlunsplit((scheme, netloc, path, new_query_string, fragment))

@app.route('/api')
def index():
    region = os.environ["NOW_REGION"]
    return json.dumps({'region':region, "status": "OK", "response": "MovR API"})

#@todo: switch this to use vehicle originiation based on the environment
@app.route('/api/<city>/vehicles.json', methods=['GET', 'POST'])
def handle_vehicles_request(city):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region,os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)

    with MovR(conn_string, echo=False) as movr:
        if request.method == 'POST':
            content = request.json
            res = movr.add_vehicle(city,
                             owner_id=content['owner_id'],
                             type=content['type'],
                             vehicle_metadata=content['vehicle_metadata'],
                             status=content['status'],
                             current_location=content['current_location'])
            return json.dumps({'region':region,'status': 'OK','response': res})
        else:
            count = 5 #request.args.get('count') #@todo: this doens't work yet.
            return json.dumps({'region':region,
                               'response': movr.get_vehicles(city, count)})

#@todo: this feels like a sharded app. need to remove city
@app.route('/api/<city>/rides/<ride_id>/locations.json', methods=['POST'])
def add_ride_location(city, ride_id):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        content = request.json
        movr.update_ride_location(city, ride_id, lat=content['lat'],
                                  long=content['long'])

        return json.dumps({})


@app.route('/api/promo_codes.json', methods=['POST'])
def create_promo_code():
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        content = request.json
        promo_code = movr.create_promo_code(
            code=content['code'],
            description=content['description'],
            expiration_time=content['expiration_time'],
            rules=content['rules'])

        return json.dumps({'promo_code': promo_code})

@app.route('/api/<city>/users/<user_id>/promo_codes.json', methods=['POST'])
def apply_promo_code(city, user_id):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        content = request.json
        movr.apply_promo_code(city, user_id,
                              content['promo_code'])
        return json.dumps({})



@app.route('/api/<city>/users.json', methods=['POST'])
def add_user(city):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        content = request.json
        movr.add_user(city,
                      content['name'],
                      content['address'],
                      content['credit_card_number'])

@app.route('/api/<city>/rides.json', methods=['POST', 'GET'])
def handle_ride_request(city):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        if request.method == 'POST':
            content = request.json
            ride = movr.start_ride(city,
                                   content['user_id'],
                                   content['vehicle_id'])

            return json.dumps({'ride': ride})
        else:
            # get active rides
            rides = movr.get_active_rides(city)
            return json.dumps({'rides': rides})


@app.route('/api/<city>/rides/<ride_id>.json', methods=['POST'])
def end_ride(city, ride_id):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region, os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)
    with MovR(conn_string, echo=False) as movr:
        movr.end_ride(city, ride_id)
        return {{}}