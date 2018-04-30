import json
import requests
import os
from .request import request
#from .config import AMADEUS_API_KEY

AMADEUS_API_KEY = os.environ['AMADEUS_API_KEY']
API_HOST = 'https://api.sandbox.amadeus.com/v1.2/'
FLIGHT_PATH = 'flights/low-fare-search'
NUMBER_OF_RESULTS = 5

def get_flights(origin, destination, departure_date, return_date=None, none_stop=None):
	"""Query the Search API by a search term and location.
    Args:
        origin: IATA City code from which the traveler will depart.
        destination: IATA code of the city to which the traveler is going
        departure_date: The date on which the traveler will depart from the origin to go to the destination.
        return_date: The date on which the traveler will depart from the destination to return to the origin.
    Returns:
        dict: The JSON response from the request.
	"""

	params = {
    	'origin': origin,
    	'destination': destination,
    	'departure_date': departure_date,
    	'return_date': return_date, 
        'nonstop': none_stop,
    	'apikey': AMADEUS_API_KEY,
    	'number_of_results': NUMBER_OF_RESULTS
    }

	flights = request(API_HOST, FLIGHT_PATH, AMADEUS_API_KEY, params)
    
	return flights

def sort_flights(flights):
    """
    This method choose the optimal round-trip flight based on price.
    Input:
        dict: self.flights

    Return:
        dict: best_flight
    """
    if "results" not in flights:
        return None
    return flights['results'][0]
