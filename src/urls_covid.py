from django.shortcuts import render
from django.urls import path
from app.src.covid import views_covid


urlpatterns = [
  

    path("dashboard/",views_covid.view_map_world,name="map_world"),
    path("dashboard/map/france/",views_covid.view_map_france,name="map_france"),
    
]