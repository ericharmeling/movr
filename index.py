from flask import Flask, Response, __version__
from flask import request
from scripts.movr import MovR
import json
import os
from urllib.parse import parse_qs, urlsplit, urlunsplit, urlencode

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
    return json.dumps({"respond": "MovR API"})

#@todo: switch this to use originiation based on the environment
@app.route('/api/vehicles/<city>.json', methods=['GET', 'PUT'])
def handle_vehicles_request(city):
    region = os.environ["NOW_REGION"]
    conn_string = connection_string_map.get(region,os.environ["MOVR_DATABASE_URL"])
    conn_string = set_query_parameter(conn_string, "application_name", region)

    with MovR(conn_string, echo=False) as movr:
        if request.method == 'PUT':
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
            return json.dumps({'region':region,'status': 'OK',
                               'response': movr.get_vehicles(city, count)})

@app.route('/api/rides/<city>/<ride_id>/locations.json', methods=['PUT'])
def add_ride_location(city, ride_id):
    with MovR(os.environ["MOVR_DATABASE_URL"], echo=False) as movr:
        content = request.json
        movr.update_ride_location(city, ride_id, lat=content['lat'],
                                  long=content['long'])

        return json.dumps({'status': "OK"})

#
# @app.route('/api/vehicles/<city>')
# def create_promo_code():
#     return {}
#
# @app.route('/api/vehicles/<city>')
# def apply_promo_code():
#     return {}
#
# @app.route('/api/vehicles/<city>')
# def add_user():
#     return {}
#
# @app.route('/api/vehicles/<city>')
# def start_ride():
#     return {}
#
# @app.route('/api/vehicles/<city>')
# def end_ride():
#     return {}