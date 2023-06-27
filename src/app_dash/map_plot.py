from os import name
from pathlib import Path
from dash import Dash,html,dcc,Input,Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
from src.app_dash.module.templateGraphPlotly import *
from src.app_dash.module.connectionDB import *
import plotly.graph_objects as go 
import plotly.express as px
from src.app_dash.app_dash_standard import *
from plotly.subplots import make_subplots
import os 
from shapely import wkt
from shapely.geometry import Point
import geopandas as gpd
from dotenv import load_dotenv
from dotenv import dotenv_values
import requests
from sqlalchemy import text
from math import *
import json
import urllib.request
load_dotenv()
config = dotenv_values(".env")


dir_app=Path(__file__).resolve().parent


password = os.getenv("mdp_connection_covid")
user = os.getenv("user_name_covid")
host = os.getenv("host")
port = os.getenv("port")
db = os.getenv("database_covid")

jt =os.getenv("jt")
px.set_mapbox_access_token(jt)

connection =ConnectionMySQL(host,port,user,password,db)
db_connection=connection.get_connection()



className={
    "graph":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full xl:w-6/12 w-max-full",
    "graph-1/3":"shadow-lg shadow-indigo-500 rounded-xl bg-white my-1 p-1 md:my-2 md:p-2 mx-1  w-full lg:w-4/12",
    "graph-full":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "graph-xl":"shadow-lg shadow-indigo-500 rounded-xl bg-white sm:m-1 sm:p-1 md:m-2 md:p-2 w-full",
    "tab_class":"bg-blue-300 border-t-0 p-3 m-2 font-semibold border-0",
    "tab_selected":"bg-white p-3 m-2 font-semibold border-0",
}
styles={
        "tab_class":{"border":"none",
                 "background":"#3b82f6",
                 "color":"#f9fafb",
                 "font-weight":"600","padding":"1em",
                 "margin":"1em",
                 "border-radius":"0.5em",
                 "max-width":"100%",
                 "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"},
    "tab_selected":{"border":"none",
                    "max-width":"100%",
                    "background":"#93c5fd",
                    "padding":"1em",
                    "margin":"1em",
                    "border-radius":"0.5em","color":"#f9fafb","font-weight":"600",
                     "box-shadow":"0 16px 26px -10px rgba(63,106,216,.56), 0 4px 25px 0 rgba(0,0,0,.12), 0 8px 10px -5px rgba(63,106,216,.2)"}


}

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

sql = text("""SELECT date_reported AS date,country,new_cases,new_deaths,cumulative_cases,cumulative_deaths FROM covid_daily""")
df = pd.read_sql_query(sql,db_connection)

def df_select_region(continent):
    df = df_bar_plot[df_bar_plot.who_region==continent]
    return df

def get_graph(df,col,continent,color):
    df=df_select_region(continent)
    df=df.groupby("date").sum(numeric_only=True).reset_index()
    # fig = px.bar(data_frame=df,x="date",y=col,color_discrete_sequence=[color])
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["date"],y=df[col],nbinsx =int(len(df)//7),histfunc="sum",name=col,marker_color=color,
                                hovertemplate='<b>'+continent+'</b>: %{y} <br>%{x}'))
    get_templates(fig)
    fig.update_layout(title=f"{region_names.get(continent)}")
    fig.update_layout(bargap=0.2)
    return fig


color_map = ["#fefce8","#fef9c3","#fef08a","#eff6ff","#dbeafe","#bfdbfe","#93c5fd","#60a5fa","#3b82f6","#2563eb","#1d4ed8","#1e40af","#1e3a8a"]


def get_df_map():
    sql_map =text("""SELECT date_reported AS date, country_code,CD.country,who_region,new_cases,cumulative_cases,new_deaths,cumulative_deaths,lat,lon
                FROM covid_daily  AS CD 
                INNER JOIN geo_country AS GC 
                ON CD.country = GC.country
                WHERE  date_reported = (SELECT MAX(date_reported) FROM covid_daily)
                ORDER BY date DESC""")
    df_map = pd.read_sql_query(sql_map,db_connection)
    return df_map
df_ =get_df_map()
df_map = df.copy()

sql_bar_plot= text("""SELECT date_reported AS date,country_code,CD.country,who_region,new_cases,cumulative_cases,new_deaths,cumulative_deaths
            FROM covid_daily AS CD""")
df_bar_plot = pd.read_sql_query(sql_bar_plot,db_connection)
df_bar_plot.date = pd.to_datetime(df_bar_plot.date,format="%Y-%m-%d")


sql_bar_all_region = text(""" 
SELECT  who_region,SUM(cumulative_cases) AS cumulative_cases,SUM(cumulative_deaths) AS cumulative_deaths 
FROM covid_daily 
WHERE date_reported = (SELECT max(date_reported) FROM covid_daily) AND who_region <> "Othher"
GROUP BY who_region """)
df_bar_all_region = pd.read_sql_query(sql_bar_all_region,db_connection)


url = "https://storage.googleapis.com/portfolio_django_web_perso/app/countries.geojson"
response = urllib.request.urlopen(url)
data_ = json.loads(response.read().decode())
data = data_.copy()


col_map = {"Nouvelle contaminations":"new_cases","Nouveaux décès":"new_deaths","Totale contamination":"cumulative_cases","Total décès":"cumulative_deaths"}

col_rename={"new_cases":"Nouvelle contaminations","new_deaths":"Nouveaux décès"}



region_names={
'EMRO':'Moyen Orient',
'EURO':'Europe',
'AFRO':'Afrique',
'WPRO':'Region Pacifique',
'AMRO':'Amerique',
'SEARO':'Asie Sud-Est',
'Other':'autre'
}

app = DjangoDash(name ='map_plot',external_stylesheets=external_stylesheets)


def get_key_number():
   # "date_reported AS date, country_code,CD.country,who_region,new_cases,cumulative_cases,new_deaths,cumulative_deaths,lat,lon"
    df = df_map.copy()
    df=df.groupby("date").agg("sum",numeric_only=True).reset_index().sort_values(by="date",ascending=False).reset_index()
 
    return html.Div(
        id="",
        children=[
            html.Div(
            children=[
                    html.Div(
                    children=[
                        html.H3(id="",children="Nouveaux cas",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.new_cases[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),

                    html.Div(
                    children=[
                        html.H3(id="",children="Total des cas ",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.cumulative_cases[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
            ],className="flex flex-col xl:flex-row p-4 m-2 bg-white xl:flex-nowrap"
            ),
            html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(id="",children="Nouveaux décès",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.new_deaths[0]))
                ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
                            html.Div(
                    children=[
                        html.H3(id="",children="Total des décès",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.cumulative_deaths[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
                    ],className="flex flex-col xl:flex-row p-4 m-2 bg-white xl:flex-nowrap"
            )
        ]
    )


@app.callback(
    Output("grah_bar_all_region","figure"),
    [Input("col","value")]
)

def graph_bar_all_region(col):
    if col == "new_cases":
        col = "cumulative_cases"
    elif col == "new_deaths":
        col = "cumulative_deaths"
    else:
        pass

    fig = px.bar(data_frame=df_bar_all_region.sort_values(by=col,ascending=False),x=col,color="who_region",y="who_region",orientation="h",color_discrete_map={
        "EMRO":"#0d9488",
        "AFRO":"#0e7490",
        "EURO":"#bef264",
        "AMRO":"#f59e0b",
        "WPRO":"#f43f5e",
        "SEARO":"#c084fc"

    },hover_name=df_bar_all_region['who_region'].apply(lambda x: region_names.get(x))
)
    fig.update_layout(
        yaxis={
            "tickmode": "array",
            "tickvals": df_bar_all_region['who_region'].unique(),
            "ticktext": [region_names.get(x, x) for x in df_bar_all_region['who_region'].unique()]
        }
    )
    get_templates(fig)
    fig.update_layout(bargap=0.5,showlegend=False,hoverlabel=dict(
    bgcolor="white",
    font_size=12,
    font_family="Arial",
    namelength=-1
    ),title=col.replace("_"," "))
    fig.update_layout(yaxis={'title':"",'visible':True, 'showticklabels':True},xaxis_visible=False,xaxis_showticklabels=False)
    fig.update_traces(hovertemplate="%{y}: %{x:,.0f}",
                      unselected={'marker': {'opacity': 0.3}})

    return fig 
@app.callback(
Output("graph_histo_all_region","figure"),
    [Input("col","value")]
)
def graph_histo_all_region(col):
    df =df_bar_plot.groupby(["date","who_region"]).sum(numeric_only=True).reset_index()
    fig = px.histogram(data_frame=df,x="date",y=col,color="who_region",nbins = int((len(df)//30)),histfunc="sum",color_discrete_map={
        "EMRO":"#0d9488",
        "AFRO":"#0e7490",
        "EURO":"#bef264",
        "AMRO":"#f59e0b",
        "WPRO":"#f43f5e",
        "SEARO":"#c084fc"

    })
    get_templates(fig)
    fig.update_layout(bargap=0.5,showlegend=False,hoverlabel=dict(
    bgcolor="white",
    font_size=12,
    font_family="Arial",
    namelength=-1
    ))
    fig.update_traces(hovertemplate="Date: %{x}<br>%{y}: %{y:,.0f}",
                      unselected={'marker': {'opacity': 0.3}})
    return fig







@app.callback(
    Output("graph_afrique","figure"),
    [Input("col","value")]
)
def graph_afrique(col):
    continent="AFRO"
    fig = get_graph(df,col,continent,color="#0e7490")
    return fig

@app.callback(Output("graph_europe","figure"),[Input("col","value")])
def graph_europe(col):
    continent="EURO"
    fig = get_graph(df,col,continent,color="#bef264")
    return fig

@app.callback(Output("graph_amerique","figure"),[Input("col","value")])
def graph_amerique(col):
    continent="AMRO"
    fig = get_graph(df,col,continent,color="#f59e0b")
    return fig

@app.callback(Output("graph_moyen_orient","figure"),[Input("col","value")])
def graph_moyen_orient(col):
    continent="EMRO"
    fig = get_graph(df,col,continent,color="#0d9488")
    return fig

@app.callback(Output("graph_pacifique","figure"),[Input("col","value")])
def graph_pacifique(col):
    continent="WPRO"
    fig = get_graph(df,col,continent,color="#f43f5e")
    return fig

@app.callback(Output("graph_asie_sud_est","figure"),[Input("col","value")])
def graph_asie_sud_est(col):
    continent="SEARO"
    fig = get_graph(df,col,continent,color="#c084fc")
    return fig

@app.callback(
    Output('map_plot','children'),
    [Input("col","value")]
)
def create_map(col,**kwargs):

    df_graph=df_map.loc[:,["country",col]]

    px.set_mapbox_access_token(jt)
    fig = px.choropleth_mapbox(df_graph,geojson=data,
                               featureidkey="properties.ADMIN",
                                mapbox_style="carto-positron",
                               locations="country",color=col,
                               opacity=0.5,color_continuous_scale=color_map,zoom=2)

    get_templates(fig)
    
    fig.update_layout(coloraxis_colorbar=dict(
    orientation='h',
    xanchor='left',
    x=0,
    yanchor='top',
    y=1,title="",len=0.25
    ),title=col,margin=dict(t=0,l=0,r=0,b=0), dragmode=False,height=800)
   
    return dcc.Graph(id="",figure=fig)

app.layout=html.Div([
    html.Div(
        children=[
            html.Div(id="key_number",children=get_key_number()),
            html.Div(
                children=[
                    dcc.Dropdown(
                        id="col",
                        options=[{"label":label.replace("_"," "),"value":value} for label,value in col_map.items() ],
                        value=col_map.get("Nouvelle contaminations"),
                      className="p-5 font-semibold text-gray-800 text-2xl ")
                ],className="w-full xl:w-1/2 p-3 m-2"
            ),
        ]),
            html.Div(id="map_plot",children=[]),
            html.Div(
                children=[
                    dcc.Graph(id="grah_bar_all_region",className="w-3/12 p-3 m-2 bg-white"),
                    dcc.Graph(id="graph_histo_all_region",className="w-9/12 p-3 m-2 bg-white"),
                ],className="flex flex-col xl:flex-row p-2 m-2 flex-nowrap justify-around items-center"
            ),
            html.Div(
                children=[  
                    dcc.Graph(id="graph_afrique",className=className.get("graph")),
                    dcc.Graph(id="graph_amerique",className=className.get("graph")),
                ],className="flex flex-col xl:flex-row flex-nowrap p-3 m-2"
            ),
               html.Div(
                children=[
                    dcc.Graph(id="graph_europe",className=className.get("graph")),
                    dcc.Graph(id="graph_moyen_orient",className=className.get("graph")),
                ],className="flex flex-col xl:flex-row flex-nowrap p-3 m-2"
            ),
               html.Div(
                children=[
                    dcc.Graph(id="graph_pacifique",className=className.get("graph")),
                    dcc.Graph(id="graph_asie_sud_est",className=className.get("graph")),
                ],className="flex flex-col xl:flex-row flex-nowrap p-3 m-2"
            ),
       
],className="bg-gray-100")


