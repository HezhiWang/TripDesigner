import datetime
import os
import pandas as pd
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, render_to_response
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
                # this is the unique_id that we created even before crawling started.
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

        form_data = final_data["form_data"]
        crawl_data = final_data["crawl_data"]
        print(form_data)




        start_address = form_data["startcity"]
        end_address = form_data["endcity"]
        destination_address = form_data["destination"]
        start_date = datetime.datetime.strptime(form_data["startdate"], "%Y-%m-%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        length = int(form_data["length"])
        end_date = start_date + datetime.timedelta(days=length)
        end_date_str = end_date.strftime("%Y-%m-%d")

        destination_lat = form_data["destinationlat"]
        destination_lng = form_data["destinationlng"]

        #call yelp api to get restaurant data
        ######. restarants = yelp_api(destination_lat, destination_lng)

        #call flights api to get flights data
        current_dir = os.path.dirname(__file__)
        airports = pd.read_csv(current_dir + '/data/airports.txt', sep=",", header=0) 

        start_city = start_address.split(",")[0]
        end_city = end_address.split(",")[0]
        destination_city = destination_address.split(",")[0]

        start_city_iatas = list(airports[airports['City'] == start_city]['IATA'])
        end_city_iatas = list(airports[airports['City'] == end_city]['IATA'])
        destination_city_iatas = list(airports[airports['City'] == destination_city]['IATA'])


        #####.  flights = get_flights(start_city_iatas[0], destination_city_iatas[0], start_date_str, end_date_str)

        #Attraction.objects.all().delete()

        template = "trip/plan.html"
        # return redirect("../login")
        return render(request, template, {})
        #return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})


def about(request):
    template = "trip/about.html"
    context = {}
    return render(request, template, context)