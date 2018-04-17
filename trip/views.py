import datetime
import os
import pandas as pd

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from scrapyd_api import ScrapydAPI
from .models import Attraction, Hotel #ScrapyItem
from uuid import uuid4

from .api.yelp_api import yelp_api, get_business, search_business
from .api.flights_api import get_flights

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
def plan(request):
    if request.method == "GET":
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)

        if not task_id or not unique_id:
            return JsonResponse({'error': 'Missing args'})

        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                # this is the unique_id that we created even before crawling started.
                attraction = Attraction.objects.get(unique_id=unique_id)
                print(attraction.to_dict['data']) 
                return JsonResponse({'data': attraction.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        else:
            return JsonResponse({'status': status})
        #return redirect("../login")
    elif request.method == "POST":

        print(request.POST)

        start_address = request.POST["startcity"]
        end_address = request.POST["endcity"]
        destination_address = request.POST["destination"]
        start_date = datetime.datetime.strptime(request.POST["startdate"], "%Y-%m-%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        length = int(request.POST["length"])
        end_date = start_date + datetime.timedelta(days=length)
        end_date_str = end_date.strftime("%Y-%m-%d")
        #enddate = 
        destination_lat = request.POST["destinationlat"]
        destination_lng = request.POST["destinationlng"]

        print(destination_lat, destination_lng)

        print(start_date_str, end_date_str)
        # call yelp api to get restaurant data
        #restarants = yelp_api(destination_lat, destination_lng)

        current_dir = os.path.dirname(__file__)

        print(start_address)
        # call flights api to get flights data
        airports = pd.read_csv(current_dir + '/data/airports.txt', sep=",", header=0) 

        start_city = start_address.split(",")[0]
        end_city = end_address.split(",")[0]
        destination_city = destination_address.split(",")[0]

        start_city_iatas = list(airports[airports['City'] == start_city]['IATA'])
        end_city_iatas = list(airports[airports['City'] == end_city]['IATA'])
        destination_city_iatas = list(airports[airports['City'] == destination_city]['IATA'])

        print(start_city_iatas)
        print(end_city_iatas)

        flights = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, end_date_str)
        print(flights)
        #Attraction.objects.all().delete()


        url = "https://www.tripadvisor.com/Attractions-g60763-Activities-New_York_City_New_York.html"

        unique_id = str(uuid4())

        print("id1", unique_id)

        settings = {
            'unique_id': unique_id, # unique ID for each record for DB
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        task = scrapyd.schedule("default", "attractioncrawler", 
                    settings=settings, url=url)


        print(Attraction.objects.all())
        #print(len(Attraction.objects.all()))
        # print(Attraction.objects.get(unique_id="e7bcf66b-42c4-4721-b2cf-9ab2c8e1c639"))
        #print(Attraction.objects.all()[len(Attraction.objects.all())-1].data)
        template = "trip/plan.html"
        return render(request, template, {})
        #return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})


def about(request):
    template = "trip/about.html"
    context = {}
    return render(request, template, context)