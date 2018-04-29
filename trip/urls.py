from django.urls import path, include, re_path
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from accounts.views import register, user_login, user_logout

from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('search', views.search, name='search'),
    path('about', views.about, name='about'),
    path('plan', views.plan, name='plan'),
    path('crawl', views.crawl, name='crawl'),
    path('error', views.error, name='error')
]

