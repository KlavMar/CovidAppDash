#import libraries
from os import name
from pathlib import Path
from dash import Dash,html,dcc,Input,Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
from src.app_dash.module.templateGraphPlotly import *
from src.app_dash.module.connectionDB import *
from src.app_dash.app_dash_standard import *
import plotly.graph_objects as go 
import plotly.express as px

from plotly.subplots import make_subplots

import os 
from shapely import wkt
from shapely.geometry import Point
import geopandas as gpd
from dotenv import load_dotenv
from dotenv import dotenv_values
from sqlalchemy import text
from math import *
load_dotenv()
config = dotenv_values(".env")


dir_app=Path(__file__).resolve().parent



password = os.getenv("mdp_connection_covid")
user = os.getenv("user_name_covid")
host = os.getenv("host")
port = os.getenv("port")
db = os.getenv("database_covid")

color_graph="#2563eb"

connection =ConnectionMySQL(host,port,user,password,db)
db_connection=connection.get_connection()

dep_pandas = pd.read_sql_query(text("SELECT DISTINCT(lib_dep) FROM covid_france"),db_connection)

sql = """SELECT * FROM covid_france 
            WHERE date = (SELECT MAX(DATE) FROM covid_france)"""
df_map_france =  pd.read_sql_query(text(sql),db_connection)

sql="SELECT * FROM covid_france"
df_fig_bar = pd.read_sql_query(text(sql),db_connection)
df_fig_bar.date = pd.to_datetime(df_fig_bar.date,format="%Y-%m-%d")
df_fig_bar["week"]=df_fig_bar.date.dt.isocalendar().week
df_fig_bar["year"]=df_fig_bar.date.dt.year
df_fig_bar["month"]=df_fig_bar.date.dt.month


app = DjangoDash(name ='map_france',external_stylesheets=external_stylesheets)


@app.callback(Output('key_number','children'),[Input("dep","value")])
def get_key_number(dep):
    df = df_map_france.copy()
    if dep is not None and len(dep)>0:
        df=df[df.lib_dep.isin(dep)].groupby("date").agg("sum").reset_index()
    else:
        df=df.groupby("date").agg({"hosp":"sum","rea":"sum","to":"mean","dchosp":"sum","incid_dchosp":"sum","incid_hosp":"sum","incid_rea":"sum"}).reset_index()
  
    return html.Div(
        id="",
        children=[
            html.Div(
            children=[
                    html.Div(
                    children=[
                        html.H3(id="",children="Hospitalisation",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.hosp[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),

                    html.Div(
                    children=[
                        html.H3(id="",children="Nouvelle Hospitalisation",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.incid_hosp[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
            ],className="flex flex-col xl:flex-row p-4 m-2 bg-white xl:flex-nowrap"
            ),
            html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(id="",children="Réanimation",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.rea[0]))
                ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
                            html.Div(
                    children=[
                        html.H3(id="",children="Nouvelles entrées en Réanimation",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df.incid_rea[0]))
                    ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/2"),
                    ],className="flex flex-col xl:flex-row p-4 m-2 bg-white xl:flex-nowrap"
            ),
                  html.Div(
            children=[
                html.Div(
            children=[
                html.H3(id="",children="Décès",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                html.P(children='{:,.0f}'.format(df.dchosp[0]))
           ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/3"),
                     html.Div(
            children=[
                html.H3(id="",children="Nouveaux  décès",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                html.P(children='{:,.0f}'.format(df.incid_dchosp[0]))
            ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/3"),

            html.Div(
            children=[
                html.H3(id="",children="Taux d'ocupation",className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                html.P(children=round((df.to*100),2)),
            ],className="flex flex-row items-center font-semibold p-3 m-2 bg-gray-100 w-full xl:w-1/3"),

            ],className="flex flex-col xl:flex-row p-4 m-2 bg-white xl:flex-nowrap"
            ),
        ]
    )

@app.callback(
    Output('map_plot_france','children'),
    [Input("col","value")]
)


def create_map(col):

    geo = gpd.GeoDataFrame.from_features(dep['features'])
    data_geo = geo['geometry'][36].centroid
  

    data_geo = Point(data_geo)
    lon = data_geo.x
    lat = data_geo.y



    df=df_map_france
    df[df.lib_reg.str.contains("Rhône")]=df[df.lib_reg.str.contains("Rhône")].replace("Auvergne et Rhône-Alpes",'Auvergne-Rhône-Alpes')
    df[df.lib_reg.str.contains("Aquitaine")]=df[df.lib_reg.str.contains("Aquitaine")].replace("Nouvelle Aquitaine",'Nouvelle-Aquitaine')
    df[df.lib_reg.str.contains("Bourgogne")]=df[df.lib_reg.str.contains("Bourgogne")].replace("Bourgogne et Franche-Comté",'Bourgogne-Franche-Comté')
    fig = px.choropleth_mapbox(data_frame=df, 
                        geojson=dep, 
                        locations='lib_dep',
                        featureidkey='properties.nom',  
                        mapbox_style="carto-positron",
                        color=col,
                        color_continuous_scale=px.colors.diverging.Temps,
                        center = {"lat": lat, "lon": lon},zoom=4.5
                        
                    )
   # fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
    fig.update_layout(coloraxis_colorbar=dict(orientation='h',xanchor='left',x=0,yanchor='top',y=1,title="",len=0.2))
    get_templates(fig)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},height=800, coloraxis_colorbar=dict(title=''),dragmode=False,title=col)
    
    return html.Div(id="",children=[dcc.Graph(id="",figure=fig)])


convert_column_name={
        "hosp":"hospitalisation",
        "rea":"réanimation",
        "dchosp":"décès Hopital",
        "incid_dchosp":"Nouveaux décés",
        "incid_hosp":"Nouveaux patients Hospitalisé (24H)",
        "incid_rea":"Nouveaux patiens en réanimation (24H)",
        "to":"Taux d'occupation",
    }


def get_df(dep):
    
    df = df_fig_bar[df_fig_bar.lib_dep.isin(dep)]
    df["dc"]= df['dchosp'].diff()

    return df
@app.callback(Output('get_graph_evol','children'),[Input("col","value"),Input("dep","value")])
def get_graph(col,dep,color=color_graph):

    if dep is not None and len(dep)>0:
        df = get_df(dep)
    else:
        df=df_fig_bar
    
    df = df[df[col]>=0]
    fig = go.Figure()
    if col == "to":
        df_graph=df.loc[:,["date",col]].groupby("date")[col].mean().reset_index()
        
    else:
        df_graph=df.loc[:,["date",col]].groupby("date")[col].sum().reset_index()

    df_graph[col] = df_graph[col].rolling(14).mean()
    fig = px.area(data_frame=df_graph,x="date",y=col,color_discrete_sequence=[color])
  
    get_templates(fig)
    fig.update_layout(title=convert_column_name.get(col))

    return html.Div(
        id="",children=
        [dcc.Graph(id="",figure=fig)])


col_dict={
    "hospitalisation":"hosp",
    "réanimation":"rea",
    "Décès":"dchosp",
    "Nouveaux décès":"incid_dchosp",
    "Taux d'occupation":"to",
    "Nombre de nouveaux patients hospitalisés (24h)":"incid_hosp",
    "Nombre de nouveaux patients admis en réanimation (24H)":"incid_rea"
}

app.layout=html.Div(

        children=[
                    html.Div(
                                    children=[
                                        html.Div(
                                            children=[
                                                html.Div(id="date",children=df_map_france.date.max(),className="text-6xl p-3 m-2 text-gray-800 font-bold"),
                                                html.Div(
                                                    id="",
                                                    children=[
                                                        html.Div(children=[

                                                            dcc.Dropdown(
                                                                id="col",
                                                                options=[{"label":i.replace("_"," "),"value":v} for i,v in col_dict.items() ],
                                                                value="hosp",
                                                                className="p-3 m-2 rounded-lg ",
                                                        ),
                                                        ],className="w-full xl: w-1/2"),
                                                        html.Div(
                                                            children=[
                                                                dcc.Dropdown(
                                                                    id="dep",
                                                                    options=[{"label":dep,"value":dep} for dep in sorted(dep_pandas.lib_dep.unique())],multi=True
                                                                    ,className="p-3 m-2 rounded-lg ")
                                                            ],className="w-full xl: w-1/2"
                                                        ),
                                                    ],className="flex flex-col xl:flex-row xl:flew-nowrap p-3 m-2 bg-white rounded-2xl"),
                                            ]),
                                html.Div(id="key_number",children=[]),
                                html.Div(
                                    children=[
                                            html.Div(id="map_plot_france",children=[],className="w-full xl:w-1/2 m-2 p-3 "),
                                            html.Div(id="get_graph_evol",children=[],className="w-full xl:w-1/2 m-2 p-3")
                                    ],className="flex flex-col xl:flex-row  flex-wrap w-full xl:flex-nowrap justify-around p-3 m-2 ")     
                ]),
],className="bg-gray-100 p-5")

