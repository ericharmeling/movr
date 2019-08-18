# misc utility functions
from flask_sqlalchemy import SQLAlchemy

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