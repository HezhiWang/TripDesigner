import googlemaps
from .config import GOOGLEMAP_KEY

def get_lat_log(attractions):
	gmaps = googlemaps.Client(key=GOOGLEMAP_KEY)
	for attraction in attractions:
		geocode_result = gmaps.geocode(attraction["name"])
		print(attraction)
		print(attraction["name"], geocode_result)
		if geocode_result is not None:
			latitude = geocode_result[0]['geometry']['location']["lat"]
			longitude = geocode_result[0]['geometry']['location']["lng"]
			attraction["latitude"] = latitude
			attraction["longitude"] = longitude
		else:
			print("HAHa")

	return attractions