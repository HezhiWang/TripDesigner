from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

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

def plan(request):
    if request.method == "GET":
        return redirect("../login")
    elif request.method == "POST":
        print(request.POST)
        template = "trip/plan.html"
        return render(request, template, {})


def about(request):
    template = "trip/about.html"
    context = {}
    return render(request, template, context)