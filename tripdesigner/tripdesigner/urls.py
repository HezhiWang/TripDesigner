"""tripdesigner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from accounts.views import register, user_login, user_logout

urlpatterns = [
	path('trip/', include('trip.urls')),
    re_path(r'^register/$', register), 
    re_path(r'^login/$', user_login), 
    re_path(r'^logout/$', user_logout), 
    path('admin/', admin.site.urls), 
    #url(r'^login/$', auth_views.login, name='login'),
    #url(r'^logout/$', auth_views.logout, name='logout'),
]

#urlpatterns += staticfiles_urlpatterns()
