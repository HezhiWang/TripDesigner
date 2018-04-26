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
from uuid import uuid4

from .models import Attraction, Hotel #ScrapyItem
from .plan import Planner
from .utils import serialize, parse_flight

from .api.yelp_api import get_restaurants, get_business, search_business
from .api.flights_api import get_flights, sort_flights
from .api.hotel_api import get_hotels, sort_hotels
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

        form_data, crawl_data, start_city, end_city, destination_city, start_date_str, length, end_date_str, destination_lat, destination_lng, start_city_iatas, end_city_iatas, destination_city_iatas = serialize(final_data)
        print(form_data)
        print(type(crawl_data))

        if crawl_data is None:
            print("crawl_data is not avaliable")
        else:
            attractions = get_lat_log(crawl_data)


            attractions_df = pd.DataFrame(attractions)

            bugdet = int(form_data["hotel"])
            degree = int(form_data["time"])

            planer = Planner(length, bugdet, degree)
            index_list, center_points, cordinate_data, recommendation_order, recommended_attractions = planer.design_attraction(attractions_df)

            print(index_list)
            # print("center_points",center_points)
            #print(cordinate_data)2018-04-23
            #print(recommendation_order)
            #print(recommended_attraction)
            # print("sds",start_date_str)
            # print("eds",end_date_str)
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%M-%d')
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%M-%d')
            # print(start_date, end_date)
            # print(start_date <= end_date)
            dates = []
            while start_date <= end_date:
                dates.append(start_date.strftime('%Y-%M-%d'))
                start_date += datetime.timedelta(days=1)
            print("dates",dates)
            #check_in = start_date_str
            #check_out = end_date.strptime('%Y-%M-%d')

            hotels = {}
            for i, center in enumerate(center_points):
                hotel = get_hotels(center[0], center[1], 1, dates[i], dates[i+1])
                best_hotel = sort_hotels(hotel)
                hotels[i] = best_hotel

            #print(hotels)

            # print(cordinate_data)
                
            recommended_attractions = recommended_attractions[["name", "hours", "location", "description", "number_of_reviews", "rating", "url"]]
            schedule = []
            restarants = {}

            for day in index_list:
                attractions, hotel, restaurant = [], [], []
                for attraction_index in index_list[day]:
                    attractions.append(recommended_attractions.iloc[attraction_index].to_dict())
                    #print(recommended_attractions.iloc[attraction_index].to_dict())

                l = len(index_list[day])
                print("length: " + str(l))
                # print(index_list[day])
                if l == 1:
                    # print(cordinate_data[index_list[day][0]][0], cordinate_data[index_list[day][0]][1])
                    restarant = get_restaurants(cordinate_data[index_list[day][0]][0], cordinate_data[index_list[day][0]][1], 2)
                    restarant_lunch, restarant_dinner = restarant.iloc[0], restarant.iloc[1]
                elif l == 2 or l== 3:
                    # print(cordinate_data[index_list[day][0]][0], cordinate_data[index_list[day][0]][1], cordinate_data[index_list[day][-1]][0], cordinate_data[index_list[day][-1]][1])
                    restarant_lunch = get_restaurants(cordinate_data[index_list[day][0]][0], cordinate_data[index_list[day][0]][1])
                    restarant_dinner = get_restaurants(cordinate_data[index_list[day][-1]][0], cordinate_data[index_list[day][-1]][1])
                elif l >= 4:
                    if l % 2 == 0:
                        # print(cordinate_data[index_list[day][l//2-1]][0], cordinate_data[index_list[day][l//2-1]][1])
                        restarant_lunch = get_restaurants(cordinate_data[index_list[day][l//2-1]][0], cordinate_data[index_list[day][l//2-1]][1])
                    else:
                        # print(cordinate_data[index_list[day][l//2]][0], cordinate_data[index_list[day][l//2]][1])
                        restarant_lunch = get_restaurants(cordinate_data[index_list[day][l//2]][0], cordinate_data[index_list[day][l//2]][1])
                    # print(cordinate_data[index_list[day][-1]][0], cordinate_data[index_list[day][-1]][1])
                    restarant_dinner = get_restaurants(cordinate_data[index_list[day][-1]][0], cordinate_data[index_list[day][-1]][1])
                else:
                    print("haha")
                    print(index_list[day])
                    continue

                restarants[i] = {"lunch": restarant_lunch, "dinner": restarant_dinner}

                schedule.append({"attractions": attractions, "hotel": hotels[day], "restaurant": {"lunch": restarant_lunch.to_dict(), "dinner": restarant_dinner.to_dict()}})

            #print(restarants)
            print(schedule)
            #trip_planer = trip_planer(1, 2, 3)
            #call yelp api to get restaurant data
            #restarants = yelp_api(destination_lat, destination_lng)

            

            # call flights api to get flights data

            flightsinfo = {
                'depart':[],
                'return':[],
                'fare': {}
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
