from pipes import Template
from django.http import HttpRequest
from django.shortcuts import render
from django_plotly_dash import DjangoDash
from django.views.generic import TemplateView
from django.conf import settings
from src.app_dash import map_plot,france_map_plot




def view_covid_graph(request):
    return render(request,"covid.html")

def view_map_world(request):
    return render(request,"map_plot.html")



def view_map_france(request):
    return render(request,'france_map.html')
