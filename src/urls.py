from django.shortcuts import render
from django.urls import path
from src import views


urlpatterns = [
  

    path("",views.view_map_world,name="map_world"),

    
]