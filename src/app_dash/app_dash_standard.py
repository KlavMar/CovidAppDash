from dash import Dash,html,dcc,Input,Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import requests
import datetime 
from sqlalchemy import text
from src.app_dash.module.templateGraphPlotly import *
color_blue = "0093D5"

#color_background="linear-gradient(45deg,#0ea5e9,#1e40af)"

className={
    "graph":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full xl:w-6/12 w-max-full",
    "graph-1/3":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full lg:w-4/12",
    "graph-full":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "graph-xl":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "tab_class":"bg-blue-300 border-t-0 p-3 m-2 font-semibold border-0",
    "tab_selected":"bg-white p-3 m-2 font-semibold border-0",
}
styles={
   "flex_center_item": {"display":"flex","flex-flow":"row wrap","align-items":"center"},
   "container_drop": {"display":"flex","flex-flow":"row wrap","align-items":"center","justify-content":"space-around"},
   "text_header":{"background-color":"#b91c1c","font-size":"1.25em","font-weight":"bold","padding":"2em","margin":"1em auto","color":"#f1f5f9",
                  "border-radius":"0.5em"},
"text_header_info":{"background-color":"#06b6d4","font-size":"1.25em","font-weight":"bold","padding":"2em","margin":"1em auto","color":"#f1f5f9",
                  "border-radius":"0.5em"},
    "dropdown":{"min-width":"30vw","font-size":"1.25em",
                            "font-weight":"bold","padding":"0.25em","margin":"1em",
                            "border-radius":"0.5em"},

    "tab_class":{"border":"none",
                 "background":"#3b82f6",
                 "color":"#f9fafb",
                 "font-weight":"600","padding":"1em",
                 "margin":"1em",
                 "border-radius":"0.5em",
                 "max-width":"90%",
                 "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"},
    "tab_selected":{"border":"none",
                    "max-width":"90%",
                    "background":"#93c5fd",
                    "padding":"1em",
                    "margin":"1em",
                    "border-radius":"0.5em","color":"#f9fafb","font-weight":"600",
                     "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"}


}

color_map = ["#fefce8","#fef9c3","#fef08a","#fde047","#eff6ff","#dbeafe","#bfdbfe","#93c5fd","#60a5fa","#3b82f6","#2563eb","#1d4ed8","#1e40af","#1e3a8a"]



geojson_reg = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
geojson_dep="https://france-geojson.gregoiredavid.fr/repo/departements.geojson"


reg=requests.get("https://france-geojson.gregoiredavid.fr/repo/regions.geojson").json()
dep= requests.get("https://france-geojson.gregoiredavid.fr/repo/departements.geojson").json()

external_stylesheets = ["https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css"]

color_kvk ="#ec4899"
color_background="#e2e8f0"
color_background_bg_plot = "rgba(255,255,255,1)"
color_background_plot = "#ffffff"
color_text  = "#475569"
color_plot = "#475569"

def get_templates(fig):
    style_graph=TemplateGraphPlotly(fig=fig,
    family_font = "Arial Black",tickangle = 0,paper_bgcolor = color_background_bg_plot ,
    plot_bg_color=color_background_plot,color = color_text,size=12,linewidth=2,linecolor = "black",color_plot=color_plot)
    fig.update_annotations(font_size=12)
    style_graph.get_template_axes()
    style_graph.get_template_layout()
    
    fig.update_yaxes(title="")
    fig.update_xaxes(title="")


    fig.update_xaxes(tickangle=45)
    return style_graph