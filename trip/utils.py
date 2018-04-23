import datetime
import os
import pandas as pd

def serialize(final_data):
    # serialize json data
    form_data = final_data["form_data"]
    crawl_data = final_data["crawl_data"]

    start_address = form_data["startcity"]
    end_address = form_data["endcity"]
    destination_address = form_data["destination"]

    start_city = start_address.split(",")[0]
    end_city = end_address.split(",")[0]
    destination_city = destination_address.split(",")[0]

    start_date = datetime.datetime.strptime(form_data["startdate"], "%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    length = int(form_data["length"])
    end_date = start_date + datetime.timedelta(days=length)
    end_date_str = end_date.strftime("%Y-%m-%d")

    destination_lat = form_data["destinationlat"]
    destination_lng = form_data["destinationlng"]

    current_dir = os.path.dirname(__file__)
    airports = pd.read_csv(current_dir + '/data/airports.txt', sep=",", header=0) 

    start_city_iatas = list(airports[airports['City'] == start_city]['IATA'])
    end_city_iatas = list(airports[airports['City'] == end_city]['IATA'])
    destination_city_iatas = list(airports[airports['City'] == destination_city]['IATA'])

    return form_data, crawl_data, start_city, end_city, destination_city, start_date_str, length, end_date_str, destination_lat, destination_lng, start_city_iatas, end_city_iatas, destination_city_iatas

def parse_flight(flights):
    parsed = []
    if flights:
        for flight in flights:
            start = flight['origin']['airport']
            end = flight['destination']['airport']
            departs_at = flight['departs_at'].replace("T"," ")
            arrives_at = flight['arrives_at'].replace("T"," ")
            number = flight['operating_airline']+flight['flight_number']
            cabin = flight['booking_info']['travel_class'].capitalize()
            parsed.append({'depart':start, 'arrive':end, 'departs_at':departs_at, 'arrives_at':arrives_at, 'number':number, 'cabin':cabin})
    return parsed