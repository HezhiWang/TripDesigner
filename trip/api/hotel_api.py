import json
import requests
from .request import request
from .config import AMADEUS_API_KEY

API_HOST = 'https://api.sandbox.amadeus.com/v1.2/'
HOTEL_PATH = 'hotels/search-circle'
NUMBER_OF_RESULTS = 5

def get_hotels(latitude, longitude, radius, check_in, check_out, all_rooms=None):
	"""Queries to see which hotels are available in a given area, on a given day and displays their lowest prices
    Args:
        latitude: Latitude of the center of the search.
        longitude: Longitude of the center of the search.
        radius: Radius around the center to look for hotels in kilometers (km).
        check_in: Date on which the guest will begin their stay in the hotel.
        check_out: Date on which the guest will end their stay in the hotel.
    Returns:
        dict: The JSON response from the request.
	"""

	params = {
    	'latitude': latitude,
    	'longitude': longitude,
    	'radius': radius,
    	'return_date': return_date, 
        'check_in': check_in,
    	'check_out': check_out,
    	'all_rooms': all_rooms,
        'number_of_results': NUMBER_OF_RESULTS
    }

	hotels = request(API_HOST, HOTEL_PATH, AMADEUS_API_KEY, params)

	print(hotels)
	return hotels

def sort_hotels(hotels):
    """
    This method choose the optimal hotel for a specific area based on price.
    Input:
        dict: hotels

    Return:
        dict: best_hotel
    """
    if "results" not in hotels:
        return None
    return hotels['results'][0]
