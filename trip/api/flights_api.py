from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib

from .request import request
from .config import AMADEUS_API_KEY

from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode

API_HOST = 'https://api.sandbox.amadeus.com/v1.2/'
FLIGHT_PATH = 'flights/low-fare-search'
NUMBER_OF_RESULTS = 50

def get_flights(origin, destination, departure_date, return_date):
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
    	'origin': 'NYC',
    	'destination': 'MSP',
    	'departure_date': '2018-05-15',
    	'return_date': '2018-05-21', 
    	'apikey': AMADEUS_API_KEY,
    	'number_of_results': NUMBER_OF_RESULTS
    }

	flights = request(API_HOST, FLIGHT_PATH, AMADEUS_API_KEY, params)

	print(flights)
	
	return flights

#get_flights("NYC", "MSP", "2018-05-15", "2018-05-23")