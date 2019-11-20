from geopy.geocoders import Nominatim

class Location():
    def __init__(self, latlong):
        geolocator = Nominatim(user_agent="movr-app")
        g = geolocator.reverse(latlong)
        city = g.raw['address']['city']
        self.city = city.lower()
        self.region = self.get_region()
    def get_region(self):
        if self.city in ('new york', 'boston', 'washington_dc'):
            return 'us_east'
        elif self.city in ('san francisco', 'seattle', 'los angeles'):
            return 'us_west'
        elif self.city in ('amsterdam', 'paris', 'rome'):
            return 'europe'
        else:
            return None
