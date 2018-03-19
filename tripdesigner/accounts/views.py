from django.contrib.auth import login, get_user_model, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import UserCreationForm, UserLoginForm

User = get_user_model()

# Create your views here.
def register(request, *args, **kwargs):
	form = UserCreationForm(request.POST or None)
	if form.is_valid():
		form.save()
		return HttpResponseRedirect("/login")
	return render(request, "accounts/register.html", {"form": form})

def user_login(request, *args, **kwargs):
	form = UserLoginForm(request.POST or None)
	if form.is_valid():
		#form.save()
		username_ = form.cleaned_data.get("username")
		user_obj = User.objects.get(username__iexact=username_)
		login(request, user_obj)
		return HttpResponseRedirect("/trip")
	return render(request, "accounts/login.html", {"form": form})

def user_logout(request):
	logout(request)
	return HttpResponseRedirect("/login")