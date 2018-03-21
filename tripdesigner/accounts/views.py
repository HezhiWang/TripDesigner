from django.contrib.auth import (
	login, 
	get_user_model, 
	logout, 
	authenticate
	)
	
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .forms import UserCreationForm, UserLoginForm

User = get_user_model()

def user_login(request):
    print(request.user.is_authenticated)
    next = request.GET.get('next')
    title = "Log In"
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect("/trip")
    return render(request, "accounts/login.html", {"form":form, "title": title})

def register(request):
    print(request.user.is_authenticated)
    next = request.GET.get('next')
    title = "Sign Up"
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect("/trip")

    context = {
        "form": form,
        "title": title
    }
    return render(request, "accounts/register.html", context)


def user_logout(request):
    logout(request)
    return redirect("/trip")

# # Create your views here.
# def register(request, *args, **kwargs):
# 	form = UserCreationForm(request.POST or None)
# 	if form.is_valid():
# 		form.save()
# 		return HttpResponseRedirect("/login")
# 	return render(request, "accounts/register.html", {"form": form})

# # def user_login(request, *args, **kwargs):
# # 	form = UserLoginForm(request.POST or None)
# # 	if form.is_valid():
# # 		#form.save()
# # 		username_ = form.cleaned_data.get("username")
# # 		user_obj = User.objects.get(username__iexact=username_)
# # 		login(request, user_obj)
# # 		return HttpResponseRedirect("/trip")
# # 	return render(request, "accounts/login.html", {"form": form})

# def user_logout(request):
# 	logout(request)
# 	return HttpResponseRedirect("/login")