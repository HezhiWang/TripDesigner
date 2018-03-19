from django.urls import path, include
#from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path('', views.index, name='index'), 
    path('search', views.search, name='search')
]

#urlpatterns += staticfiles_urlpatterns()
