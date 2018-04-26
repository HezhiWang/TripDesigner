import googlemaps
from .config import GOOGLEMAP_KEY

def get_lat_log(attraction):
	gmaps = googlemaps.Client(key=GOOGLEMAP_KEY)
	#for attraction in attractions:
	geocode_result = gmaps.geocode(attraction["name"])
	#print(attraction)
	#print(attraction["name"], geocode_result)
	if geocode_result != []:
		latitude = geocode_result[0]['geometry']['location']["lat"]
		longitude = geocode_result[0]['geometry']['location']["lng"]
		attraction["latitude"] = latitude
		attraction["longitude"] = longitude
	else:
		#attractions.remove(attraction)
		print(geocode_result)
		print("HAHA")

	return attraction
