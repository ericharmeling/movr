# The Location class holds information about regions, cities, and addresses
from flask import request
import requests
import json
import geocoder

class Location():
    def __init__(self, debug=True):
        if debug==False: 
            ip = request.remote_addr
            g = geocoder.ip(ip)
            city = g.city
            current_location= g.latlng
        else:
            city = 'new york'
            current_location = '23rd Street'
        self.city = city
        self.region = self.get_region()
        self.current = current_location
    def get_region(self):
        if self.city in ('new_york', 'boston', 'washington_dc'):
            return 'us_east'
        elif self.city in ('san_francisco', 'seattle', 'los_angeles'):
            return 'us_west'
        elif self.city in ('chicago', 'detroit', 'minneapolis'):
            return 'us-mid'
        elif self.city in ('amsterdam', 'paris', 'rome'):
            return 'europe'
        else:
            return None
            