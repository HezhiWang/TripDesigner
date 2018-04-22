# https://github.com/Yelp/yelp-fusion/blob/master/fusion/python/sample.py as reference
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import time
import pandas as pd

from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
from functools import partial
from multiprocessing.pool import Pool

from .request import request
from .config import YELP_API_KEY

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'Chinese'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 10
NUMBER_OF_PROCESS = 2
LAT = 40.7127753
LNG = -74.0059728

def search_business(api_key, latitude, longitude, offset):
    """Query the Search API by a search term and location.
    Args:
        latitude (decimal): The latitude of the business to the API.
        longitude (decimal): The longitude of the business to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'latitude': latitude, 
        'longitude': longitude,
        'limit': SEARCH_LIMIT, 
        'offset': offset
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id_list):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    fields = ["id", "name", "url", "display_phone", "review_count", "rating", "location", "coordinates", "price"]
    restarants = []

    for business_id in business_id_list:
        business_path = BUSINESS_PATH + business_id
        response = request(API_HOST, business_path, api_key)
        business = {}
        for field in fields:
            if field == "coordinates":
                business["latitude"] = response["coordinates"]["latitude"]
                business["longitude"] = response["coordinates"]["longitude"]
            elif field == "location":
                business["address"] = response["location"]["display_address"]
            elif field in response:
                business[field] = response[field]
            else:
                business[field] = None

        restarants.append(business)
    
    return restarants


def get_restaurants(latitude, longitude, number_of_best=1):
    """Queries the API by the input values from the user.
    Args:
        latitude (decimal): The latitude of the business to query.
        longitude (decimal): The longitude of the business to query.
    """
    business_id_list = []
    for offset in range(0, 100, 50):
        print(offset)
        response = search_business(YELP_API_KEY, latitude, longitude, offset)

        businesses = response.get('businesses')

        for business in response['businesses']:
            business_id_list.append(business["id"])

    if not businesses:
        print(u'No businesses found.')
        return

    restarants = get_business(YELP_API_KEY, business_id_list) 

    restarants = pd.DataFrame(restarants)

    #sort by review_count, rating
    restarants.sort_values(by=["review_count", "rating"], inplace=True)

    #print(restarants)
    print(restarants.shape)
    if (number_of_best > 1):
        return restarants[number_of_best]
    return restarants[0]


################# Multiprocessing version #################

"""

def get_business(api_key, business_id_list):
    # Query the Business API by a business ID.
    # Args:
    #     business_id (str): The ID of the business to query.
    # Returns:
    #     dict: The JSON response from the request.
    fields = ["id", "name", "url", "display_phone", "review_count", "rating", "location", "coordinates", "price"]
    restarants = []

    print(business_id_list)

    #for business_id in business_id_list:
    print(business_id_list)
    business_path = BUSINESS_PATH + business_id_list
    print(business_path)
    response = request(API_HOST, business_path, api_key)
    print(response)
    business = {}
    for field in fields:
        if field == "coordinates":
            business["latitude"] = response["coordinates"]["latitude"]
            business["longitude"] = response["coordinates"]["longitude"]
        elif field == "location":
            business["address"] = response["location"]["display_address"]
        elif field in response:
            business[field] = response[field]
        else:
            business[field] = None

    restarants.append(business)
    
    return restarants


def yelp_api(latitude, longitude):
    # Queries the API by the input values from the user.
    # Args:
    #     latitude (decimal): The latitude of the business to query.
    #     longitude (decimal): The longitude of the business to query.

    business_id_list = []
    for offset in range(0, 100, 50):
        print(offset)
        response = search_business(API_KEY, latitude, longitude, offset)

        businesses = response.get('businesses')

        for business in response['businesses']:
            business_id_list.append(business["id"])

    if not businesses:
        print(u'No businesses found.')
        return

    print(business_id_list)
    get_businesses = partial(get_business, API_KEY)
    #get_business(API_KEY, business_id_list)

    with Pool(NUMBER_OF_PROCESS) as p:
        restarants = p.map(get_businesses, business_id_list)

    #restarants = get_business(API_KEY, business_id_list) 

    #restarants = pd.DataFrame(restarants)

    print(restarants)
    print(restarants.shape)

    return restarants
"""







def multi_processes_check():
    ts = time()


    print('Took {}s'.format(time() - ts))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location',
                        default=DEFAULT_LOCATION, type=str,
                        help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    #print(input_values)
    start_time = time.time()
    try:
        restarants = yelp_api(LAT, LNG)
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )
    print(time.time() - start_time)

if __name__ == '__main__':
    main()