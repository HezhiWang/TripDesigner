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
        print(attraction_htmls)
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

        attractions = get_lat_log(crawl_data)


        attractions_df = pd.DataFrame(attractions)


        planer(length, )

        #trip_planer = trip_planer(1, 2, 3)
        #call yelp api to get restaurant data
        #restarants = yelp_api(destination_lat, destination_lng)

        # call flights api to get flights data

        # if start city is the same as end city
        if (start_city_iatas[0] == end_city_iatas[0]):
            flights = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, end_date_str, False)
            best_flight = sort_flights(flights)
        else:
            flight1 = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, None, False)
            flight2 = get_flights(destination_city_iatas[0], end_city_iatas[0], end_date_str, None, False)
            best_flight1 = sort_flights(flight1)
            best_flight2 = sort_flights(flight2)
        
            print(best_flight1)
            print(best_flight2)

        print(best_flight)

        #TODO: calculate daily schedule - k means
        #suggested saving format: 
        schedule = [
        {'flight':[start_city, destination_city, "05:10", "08:20","$210.00"],
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

        {'flight':[],
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
            "range":range(length),
            "schedule": schedule, 
            "destination": destination_city
        }
        # return redirect("../login")
        return render(request, template, context)
        #return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})


def about(request):
    template = "trip/about.html"
    context = {}
    return render(request, template, context)

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
