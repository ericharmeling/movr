from flask import Flask, Response, __version__
from scripts.movr import MovR
import json

app = Flask(__name__)
source = 'https://github.com/zeit/now-examples/tree/master/python-flask'
css = '<link rel="stylesheet" href="/css/style.css" />'

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    with MovR("cockroachdb://root@34.73.21.4:26257/movr?sslmode=disable", echo=False) as movr:
        return json.dumps({'vehicles': movr.get_vehicles("new york", 25)})

    #return json.dumps({'status': 'OK!'})
