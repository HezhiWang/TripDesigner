import datetime
import os
import pandas as pd
import json
import googlemaps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from scrapyd_api import ScrapydAPI
from .models import Attraction, Hotel #ScrapyItem
from uuid import uuid4
from .plan import *

from .api.yelp_api import yelp_api, get_business, search_business
from .api.flights_api import get_flights, sort_flights
from .api.googlemap import get_lat_log

scrapyd = ScrapydAPI('http://localhost:6800')

#from .models import Question

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #template = loader.get_template('trip/landing.html')
    #context = {
    #    'latest_question_list': latest_question_list,
    #}

    #template = loader.get_template("trip/landing.html")
    template = "trip/landing.html"
    context = {}
    return render(request, template, context)

def search(request):
    # if request.method == "GET":
    if request.user.is_authenticated:
        template = "trip/search.html"
    else:
        template = "../login"
        return redirect(template)
    context = {}
    return render(request, template, context)
    # elif request.method == "POST":
    #     print(request.POST)
    #     template = "trip/plan.html"
    #     return render(request, template, {})

@csrf_exempt
def crawl(request):
    if request.method == "GET":
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        status = scrapyd.job_status('default', task_id)
        print(status)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.\
                attraction = Attraction.objects.get(unique_id=unique_id)
                print("get number of attractions: " + str(len(attraction.to_dict['data'])))
                return JsonResponse({'data': attraction.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})
        #return redirect("../login")
    elif request.method == "POST":

        print(request.POST)

        destination_address = request.POST["destination"]
        destination_city = destination_address.split(",")[0]

        current_dir = os.path.dirname(__file__)
        airports = pd.read_csv(current_dir + '/data/airports.txt', sep=",", header=0) 

        attraction_htmls = list(airports[airports["City"] == destination_city]["Attraction_html"])
        #print(attraction_htmls)
        if len(attraction_htmls) == 0:
            ### display alert no avaliable city
            print("Error: no avaliable city")
        else:
            url = attraction_htmls[0]

        unique_id = str(uuid4())

        settings = {
            'unique_id': unique_id, # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        task = scrapyd.schedule("default", "attractioncrawler", 
                    settings=settings, url=url)

        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

@csrf_exempt
def plan(request):
    if request.method == "GET":
        return redirect("../login")
    elif request.method == "POST":
        final_data = json.loads(request.POST['finaldata'])

        crawl_data, start_city, end_city, destination_city, start_date_str, length, end_date_str, destination_lat, destination_lng, start_city_iatas, end_city_iatas, destination_city_iatas = serialize(final_data)
        
        #print(crawl_data)

        #attractions = get_lat_log(crawl_data)


        #attractions_df = pd.DataFrame(attractions)


        #planer(length, )

        #trip_planer = trip_planer(1, 2, 3)
        #call yelp api to get restaurant data
        #restarants = yelp_api(destination_lat, destination_lng)

        # call flights api to get flights data

        # if start city is the same as end city
        flightsinfo = {
        'depart':[],
        'return':[],
        'fare': {}
        }

        x = {'itineraries': 
        [
        {'inbound': {'flights': [{'origin': {'airport': 'LGA', 'terminal': 'A'}, 'arrives_at': '2018-04-27T21:30', 'departs_at': '2018-04-27T18:15', 'operating_airline': 'AS', 'marketing_airline': 'AS', 'booking_info': {'booking_code': 'H', 'travel_class': 'ECONOMY', 'seats_remaining': 4}, 'destination': {'airport': 'DAL', 'terminal': '1'}, 'aircraft': 'E75', 'flight_number': '3327'}, {'origin': {'airport': 'DAL', 'terminal': '1'}, 'arrives_at': '2018-04-28T09:18', 'departs_at': '2018-04-28T07:30', 'operating_airline': 'AS', 'marketing_airline': 'AS', 'booking_info': {'booking_code': 'R', 'travel_class': 'ECONOMY', 'seats_remaining': 2}, 'destination': {'airport': 'SFO', 'terminal': '0'}, 'aircraft': '32S', 'flight_number': '1713'}]}, 
        'outbound': {'flights': [{'origin': {'airport': 'SFO', 'terminal': '1'}, 'arrives_at': '2018-04-22T12:09', 'departs_at': '2018-04-22T06:30', 'operating_airline': 'DL', 'marketing_airline': 'DL', 'booking_info': {'booking_code': 'Q', 'travel_class': 'ECONOMY', 'seats_remaining': 9}, 'destination': {'airport': 'MSP', 'terminal': '1'}, 'aircraft': '753', 'flight_number': '1847'}, {'origin': {'airport': 'MSP', 'terminal': '1'}, 'arrives_at': '2018-04-22T16:43', 'departs_at': '2018-04-22T13:02', 'operating_airline': 'DL', 'marketing_airline': 'DL', 'booking_info': {'booking_code': 'Q', 'travel_class': 'ECONOMY', 'seats_remaining': 9}, 'destination': {'airport': 'LGA', 'terminal': 'D'}, 'aircraft': '320', 'flight_number': '1784'}]}}
        ], 
        'fare': {'restrictions': {'change_penalties': True, 'refundable': False}, 'total_price': '816.60', 'price_per_adult': {'tax': '99.39', 'total_fare': '816.60'}}
        }
        y = {'fare': {'total_price': '208.40', 'price_per_adult': {'total_fare': '208.40', 'tax': '40.96'}, 'restrictions': {'change_penalties': True, 'refundable': False}}, 
        'itineraries': 
        [
        {'outbound': {'flights': [{'marketing_airline': 'F9', 'flight_number': '670', 'aircraft': '320', 'origin': {'terminal': '1', 'airport': 'SFO'}, 'operating_airline': 'F9', 'departs_at': '2018-04-25T00:59', 'arrives_at': '2018-04-25T04:29', 'booking_info': {'travel_class': 'ECONOMY', 'booking_code': 'M', 'seats_remaining': 4}, 'destination': {'airport': 'DEN'}}, {'marketing_airline': 'F9', 'flight_number': '506', 'aircraft': '320', 'origin': {'airport': 'DEN'}, 'operating_airline': 'F9', 'departs_at': '2018-04-25T11:12', 'arrives_at': '2018-04-25T17:00', 'booking_info': {'travel_class': 'ECONOMY', 'booking_code': 'M', 'seats_remaining': 4}, 'destination': {'terminal': 'D', 'airport': 'LGA'}}]}}
        ]
        }
        if (start_city_iatas[0] == end_city_iatas[0]):
            flights = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, end_date_str, False)
            best_flight = sort_flights(flights)
            if best_flight:
                departf = best_flight['itineraries'][0]['outbound']['flights']
                returnf = best_flight['itineraries'][0]['inbound']['flights']
                flightsinfo['depart'] = parse_flight(departf)
                flightsinfo['return'] = parse_flight(returnf)
                flightsinfo['fare'] = {'total': best_flight['fare']['total_price'], 'tax':best_flight['fare']['price_per_adult']['tax']}
        else:
            flight1 = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, None, False)
            flight2 = get_flights(destination_city_iatas[0], end_city_iatas[0], end_date_str, None, False)
            best_flight1 = sort_flights(flight1)
            best_flight2 = sort_flights(flight2)
            try:
                departf = best_flight1['itineraries'][0]['outbound']['flights']
                total1 = float(best_flight1['fare']['total_price'])
                tax1 = float(best_flight1['fare']['price_per_adult']['tax'])
            except:
                departf = None
                total1 = 0
                tax1 = 0
            try:
                returnf = best_flight2['itineraries'][0]['outbound']['flights']
                total2 = float(best_flight2['fare']['total_price'])
                tax2 = float(best_flight2['fare']['price_per_adult']['tax'])
            except:
                returnf = None
                total2 = 0
                tax2 = 0
            flightsinfo['depart'] = parse_flight(departf)
            flightsinfo['return'] = parse_flight(returnf)
            flightsinfo['fare'] = {'total': round(total1+total2,2), 'tax':round(tax1+tax2,2)}

        print(flightsinfo)

        #TODO: calculate daily schedule - k means
        #suggested saving format: 
        schedule = [
        {
        'attractions':
            [
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"},
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"},
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"}
            ],
        'hotel':
            [
                {'name':"414 Hotel", 'score': "9.4","reviews":"287", "address":"414 West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$260"},
                {'name':"414 Hotel", 'score': "9.4","reviews":"287", "address":"414 West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$260"}

            ],
        'restaurant':
            [
                {'name':"D'Amore Winebar & Ristorante", 'type': "French","score":"5","reviews":"153", "address":"West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$$$$"},
                {'name':"D'Amore Winebar & Ristorante", 'type': "French","score":"5","reviews":"153", "address":"West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$$$$"}
            ],
        },

        {
        'attractions':
            [
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"},
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"},
                {'name':"The Metropolitan Museum of Art", 'time': "2-3 hours","address":"1000 5th Ave, New York City, NY 10028-0198","desc": "A museum"}
            ],
        'hotel':
            [
                {'name':"414 Hotel", 'score': "9.4","reviews":"287", "address":"414 West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$$"}
            ],
        'restaurant':
            [
                {'name':"D'Amore Winebar & Ristorante", 'type': "French","score":"5","reviews":"153", "address":"West 46 Street, Hell's Kitchen, New York City, NY 10036, United States of America","price": "$$$$"}
            ]
        }

        ]
        template = "trip/plan.html"
        context={
            "flight":flightsinfo,
            "schedule": schedule, 
            "destination": destination_city
        }
        return render(request, template, context)


def about(request):
    template = "trip/about.html"
    context = {}
    return render(request, template, context)

# utils
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

    return crawl_data, start_city, end_city, destination_city, start_date_str, length, end_date_str, destination_lat, destination_lng, start_city_iatas, end_city_iatas, destination_city_iatas

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
