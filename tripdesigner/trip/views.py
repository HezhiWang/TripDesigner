from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import loader

#from .models import Question


def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #template = loader.get_template('trip/landing.html')
    #context = {
    #    'latest_question_list': latest_question_list,
    #}
    template = loader.get_template("trip/landing.html")
    return HttpResponse(template.render())

def search(request):

	template = loader.get_template("trip/search.html")
	return HttpResponse(template.render())