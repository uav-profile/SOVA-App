#import opencellid
from math import cos, sqrt, pi
from pprint import pprint
import json
import requests

def GetCoordinates(token = None, text = None):
    string_to_return = ""
    limit = ""
    url = "https://us1.unwiredlabs.com/v2/search.php"
    data = {
        'token': token,
        'q': text
    }
    response = requests.get(url, params=data)
    data = response.json()
    limit = str(data.get("balance"))
    try:
        try:
            adress_dict = data.get("address")
            if adress_dict != None:
                count = 1
                for item in adress_dict:
                    title = item.get("display_name")
                    latt = item.get("lat")
                    lonn = item.get("lon")
                    if count == 1:
                        string_to_return += ("<b>" + str(count) + ".</b> "+ str(latt) + ", " + str(lonn) + ": " + title)
                    else:
                        string_to_return += ("<br><b>" + str(count) + ".</b> " + str(latt) + ", " + str(
                            lonn) + ": " + title + "</br>")
                    count = count + 1
        except Exception as e:
            print(e)
    except Exception as err:
        string_to_return = str(err)
    return string_to_return, limit

def GetInfoByCoordinates(token = None, latit = None, longit = None):
    string_to_return = ""
    limit = ""
    url = "https://us1.unwiredlabs.com/v2/reverse.php"
    data = {
        'token': token,
        'lat': latit,
        'lon': longit
    }
    response = requests.get(url, params=data)
    data = response.json()
    try:
        try:
            limit = str(data.get("balance"))
            adress_dict = data.get("address")
            if adress_dict != None:
                if len(adress_dict):
                    try:
                        string_to_return = adress_dict["display_name"]
                    except:
                        city = adress_dict.get("city")
                        region = adress_dict.get("state")
                        country = adress_dict.get("country")
                        neighbour = adress_dict.get("neighbourhood")
                        if city != None:
                            string_to_return += city
                        if region != None:
                            string_to_return += (", " + region)
                        if country != None:
                            string_to_return += (", " + country)
                        if neighbour != None:
                            string_to_return += ("; " + neighbour)
        except:
            string_to_return = data.get("message")
    except Exception as err:
        string_to_return = str(err)
    return string_to_return, limit

class Coord:
    def __init__(self, lat=0.0, lon=0.0):
        self.lat = lat
        self.lon = lon

    # Constructor to parse coordinates from string in format: 'lat,lon'
    @classmethod
    def from_str(self, s):
        try:
            lat, lon = map(float, s.split(','))
            return self(lat, lon)
        except ValueError:
            print("Error: could not parse location, quitting.")
            quit()

    # Takes number of decimal numbers, default 5
    # Returns Cooridnate as str in format: lat,lon
    def to_str(self, d=5):
        return str(round(self.lat, d)) + ',' + str(round(self.lon, d))

    # Takes a  area size in km^2.
    # Returns coordiantes of the corners of the sqare with given area,
    # surrounding the center
    def square_from_point(self, area=1.0):
        c = 111.3  # km/°
        a = sqrt(area) / 2  # km

        lat_del = a / c
        lon_del = a / (c * cos(self.lat * (pi / 180)))

        p_max = Coord(self.lat + lat_del, self.lon + lon_del)
        p_min = Coord(self.lat - lat_del, self.lon - lon_del)
        return (p_max, p_min)