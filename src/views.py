from pipes import Template
from django.http import HttpRequest
from django.shortcuts import render
from django_plotly_dash import DjangoDash
from django.views.generic import TemplateView
from django.conf import settings
from src.app_dash import map_plot






def view_map_world(request):
    return render(request,"map_plot.html")


