import googlemaps
from .config import GOOGLEMAP_KEY

def get_lat_log(attraction):
	gmaps = googlemaps.Client(key=GOOGLEMAP_KEY)
	geocode_result = gmaps.geocode(attraction["name"])
	if geocode_result != []:
		latitude = geocode_result[0]['geometry']['location']["lat"]
		longitude = geocode_result[0]['geometry']['location']["lng"]
		attraction["latitude"] = latitude
		attraction["longitude"] = longitude
	else:
		print(geocode_result)

	return attraction

