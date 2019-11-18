import geocoder

class Location():
    def __init__(self, ip=None, city=None):
        if ip:
            g = geocoder.ip(ip)
            city = g.city
        elif city:
            city=city
        self.city = city
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
