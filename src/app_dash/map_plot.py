from os import name
from pathlib import Path
from dash import Dash,html,dcc,Input,Output,ctx,callback
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
from src.app_dash.module.templateGraphPlotly import *
from src.app_dash.module.connectionDB import *
import plotly.graph_objects as go 
import plotly.express as px

import os 

from dotenv import load_dotenv
from dotenv import dotenv_values

from sqlalchemy import text

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



color_kvk ="#ec4899"
color_background="#e2e8f0"
color_background_bg_plot = "rgba(255,255,255,1)"
color_background_plot = "#ffffff"
color_text  = "#475569"
color_plot = "#475569"

def get_templates(fig):
    style_graph=TemplateGraphPlotly(fig=fig,
    family_font = "Arial Black",tickangle = 0,paper_bgcolor = color_background_bg_plot ,
    plot_bg_color=color_background_plot,color = color_text,size=14,linewidth=4,linecolor="black",color_plot=color_plot)
    fig.update_annotations(font_size=14)
    style_graph.get_template_axes()
    style_graph.get_template_layout()
    
    fig.update_yaxes(title="")
    fig.update_xaxes(title="")


    fig.update_xaxes(tickangle=45)
    return style_graph





def get_df_map():
    sql_map =text("""SELECT date_reported AS date, country_code,CD.country,who_region,new_cases,cumulative_cases,new_deaths,cumulative_deaths,lat,lon
                FROM covid_daily  AS CD 
                INNER JOIN geo_country AS GC 
                ON CD.country = GC.country
                WHERE  date_reported = (SELECT MAX(date_reported) FROM covid_daily) AND who_region != 'Other'
                ORDER BY date DESC""")
    df_map = pd.read_sql_query(sql_map,db_connection)
    return df_map

region_names={
'EMRO':'Moyen Orient',
'EURO':'Europe',
'AFRO':'Afrique',
'WPRO':'Region Pacifique',
'AMRO':'Amerique',
'SEARO':'Asie Sud-Est',
'Other':'autre'
}


df_ =get_df_map()
df_["who_region"]=df_["who_region"].apply(lambda x:region_names.get(x))
region_name = df_["who_region"].drop_duplicates()

region_ids = [region.lower().replace(" ","_") for region in df_["who_region"].drop_duplicates()]
df_=df_.rename(columns={"who_region":"Région","new_cases":"Cas","cumulative_cases":"Total des cas","new_deaths":"Décès","cumulative_deaths":"Total des décès"})

color=[ "#0d9488","#0e7490","#bef264","#f59e0b","#f43f5e","#c084fc"]

color_map = dict(zip(region_name, color))


req_global= text("""SELECT date_reported AS date,country_code,CD.country,who_region AS Région,new_cases AS Cas,cumulative_cases AS 'Total des cas',new_deaths  AS Décès, cumulative_deaths AS 'Total des Décès',
 ROUND((cumulative_deaths/cumulative_cases)*100,2)  AS 'Taux de létalité'
            FROM covid_daily AS CD
            WHERE cumulative_deaths > 0 AND cumulative_cases >0 AND  cumulative_cases > cumulative_deaths""")
df_global = pd.read_sql_query(req_global,db_connection)
df_global.date = pd.to_datetime(df_global.date,format="%Y-%m-%d")
df_global["Région"]=df_global["Région"].apply(lambda x:region_names.get(x))


sql_bar_all_region = text(""" 
SELECT  who_region,SUM(cumulative_cases) AS 'Total des cas' ,SUM(cumulative_deaths) AS 'Total des décès'
FROM covid_daily 
WHERE date_reported = (SELECT max(date_reported) FROM covid_daily) AND who_region != "Other"
GROUP BY who_region """)
df_bar_all_region = pd.read_sql_query(sql_bar_all_region,db_connection)




cols = ["Cas","Décès"]
subs_cols=["Total"]
col_rename={"new_cases":"Nouvelle contaminations","new_deaths":"Nouveaux décès"}


def get_dropdown():
    list_div = html.Div(children=[],className="flex flex-col p-2 m-3")

    dict_drop = {"col":cols,"sub_cols":subs_cols}


    for id_name,value_drop in dict_drop.items():
        list_div.children.append(
                dcc.Dropdown(
                        id=id_name,
                        options=[{"label":value,"value":value} for value in value_drop ],
                        value=value_drop[0],
                        className="font-medium text-lg p-2 m-2 text-gray-700  ",
                        ),
        )

    return list_div


external_stylesheets = ['https://cdn.jsdelivr.net/npm/tailwindcss/dist/tailwind.min.css']
app = DjangoDash(name ='map_plot',external_stylesheets=external_stylesheets)

@app.callback(Output("key_number","children"),[Input("col","value"),Input("region_name","value")])
def get_key_number(col,region_name):
    df = df_

    if region_name is None:
        pass 
    else:
        df=df[df["Région"]==region_name]

    df=df.groupby("date").agg("sum",numeric_only=True).reset_index().sort_values(by="date",ascending=False).reset_index()

    df=df[df.date==max(df.date)]
    if col == "Cas":
        cols_names = {
            "Nouveaux cas":{
                "col":"Cas","class":"border-green-400"
            },
            "Total des cas":{
                "col":"Total des cas","class":"border-green-400"
            }
        }
    elif col == "Décès":
        cols_names = {
                "Nouveaux décès":{
                    "col":"Décès","class":"border-red-400"
                },
                "Total des décès":{
                    "col":"Total des décès","class":"border-red-400"
                },
        }
    bloc=html.Div(children=[],className="flex flex-col ")
    for name,value in cols_names.items():
        bloc.children.append(
                    html.Div(
                    children=[
                        html.H3(id="",children=name,className="p-3 m-2 font-semibold text-2xl text-gray-700"),
                        html.P(children='{:,.0f}'.format(df[value.get("col")][0]),className="p-3 m-2")
                    ],className=f"flex flex-row items-center font-semibold p-3 m-2 bg-white border-l-4 {value.get('class')} w-full col-span-3"),
        )
    return bloc



def create_btn():
    region_name = df_["Région"].drop_duplicates()

    return   html.Div(
        children=[
            dcc.Dropdown(
                        id="region_name",
                        options=[{"label":region,"value":region} for  region in region_name],
                        value=None,
                        placeholder="Sélectionnez une région",
                       className="font-medium text-lg p-2 m-2 text-gray-700  "
                        
                        
                    )
        ],className="flex flex-col p-2 m-3")




@app.callback(Output("grah_bar_all_region","figure"),[Input("col","value"),Input("region_name","value")])

def graph_bar_all_region(col,region_name):
    df_bar_all_region=df_.groupby("Région").agg("sum").reset_index()

    if region_name is None:
        pass
    else:
        df_bar_all_region=df_bar_all_region[df_bar_all_region["Région"]==region_name]

    if col == "Cas":
        col = "Total des cas"
    elif col == "Décès":
        col = "Total des décès"
    else:
        pass

    fig = px.bar(data_frame=df_bar_all_region.sort_values(by=col,ascending=False),x=col,color="Région",y="Région", text_auto='.2s',
        orientation="h",color_discrete_map=color_map,opacity=0.5)

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

@app.callback(Output("letal_rate","children"),[Input("region_name","value")])

def get_letal_rate(region_name):

    if region_name == None:
        df=df_global.groupby(["date","Région"]).mean(numeric_only=True).reset_index()
    else:
        df=df_global[df_global["Région"]==region_name].groupby(["date","Région"]).mean(numeric_only=True).reset_index()
    df['year'] = df['date'].dt.year
    df['trimestre'] = df['date'].dt.quarter
    df = df.groupby(["year","trimestre","Région"])["Taux de létalité"].mean(numeric_only="True").reset_index()
    quarter_mapping = {1: 'T1', 2: 'T2', 3: 'T3', 4: 'T4'}
    df.trimestre = df.trimestre.map(quarter_mapping)
    df=df.astype({"year":"str","trimestre":"str"})

    df["year_trimestre"] = df.year+" "+df.trimestre
    fig = px.bar(df,x="year_trimestre",y="Taux de létalité",color="Région",color_discrete_map=color_map)
    get_templates(fig)
   

    fig.update_layout(showlegend=False,title="Taux de létalité (moyen)",barmode="group")
    return html.Div(
        children=[
            dcc.Graph(figure=fig)
        ]
    )
@app.callback(Output("graph_histo_all_region","children"),[Input("col","value"),Input("region_name","value")])
def graph_histo_all_region(col,region_name):
    df =df_global.groupby(["date","Région"]).sum(numeric_only=True).reset_index()
    if region_name is  None:
        pass
    else:
        df=df[df["Région"] == region_name]
    fig = px.histogram(data_frame=df,x="date",y=col,color="Région",nbins = int((len(df)//30)),histfunc="sum",color_discrete_map=color_map)
    get_templates(fig)
    fig.update_layout(title=col)
    fig.update_layout(bargap=0.5,showlegend=False,hoverlabel=dict(
    bgcolor="white",
    font_size=12,
    font_family="Arial",
    namelength=-1
    ))
    fig.update_traces(hovertemplate="Date: %{x}<br>%{y}: %{y:,.0f}",
                      unselected={'marker': {'opacity': 0.3}})
    
    return html.Div(
        children=[
            dcc.Graph(figure=fig)
        ]
    )











@app.callback(Output('map_plot','children'),[Input("col","value"),Input("sub_cols","value"),Input("region_name","value")])

def create_map(col,sub_cols,region_name,**kwargs):
    df = df_
  #  df["Région"]=df["Région"].str.lower().str.replace(" ","_")
    if col == "Cas":
        df = df.loc[:, ["Région", "lat", "lon", "country"] + list(df_.filter(like='cas').columns)]
        if sub_cols == "Total":
          col = "Total des cas"
        else:
            col="cas"
    elif col == "Décès":
        df = df.loc[:, ["Région", "lat", "lon", "country"] + list(df_.filter(like='décès').columns)]

        if sub_cols == "Total":
          col = "Total des décès"

        else:
            col="décès"
  



    if region_name is  None or len(region_name) ==0:
        df=df
    else:
        df=df[df["Région"]==region_name]
    px.set_mapbox_access_token(jt)
    fig = px.scatter_mapbox(df, color="Région",   mapbox_style="carto-positron", lat=df.lat,lon=df.lon,zoom=2,size=col, size_max=150,
                           color_discrete_map=color_map,opacity=0.5,
                            hover_name="country",custom_data=["country","Région",col])

    fig.update_layout(height=800,margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_layout(legend=dict(orientation='h',xanchor='left',x=0,yanchor='top',y=1,title=""))
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Sans-serif"
        )
    )

    return dcc.Graph(figure=fig,className="")

app.layout=html.Div([
    #    html.Div(id="listcheck",children=create_btn()),
    
    html.Div(
        children=[
          
            
        ]),
            html.Div(children=[
            html.Div(id="map_plot",children=[]),
            html.Div(
            children=[
                create_btn(),
                get_dropdown(),
                        html.Div(id="key_number",children=[]),
            ],  className="w-1/6 overflow-hidden absolute top-50 left-0 bottom-0 h-max bg-white opacity-0.8 rounded-2xl "
        )
            ],className="relative"
            ),
           
            html.Div(
                children=[
                    dcc.Graph(id="grah_bar_all_region",className="w-full xl:col-span-4 p-3 m-2 bg-white"),
                    html.Div(id="letal_rate",children=[],className="w-full xl:col-span-4 p-3 m-2 bg-white"),
                    html.Div(id="graph_histo_all_region",children=[],className="w-full xl:col-span-4 p-3 m-2 bg-white")
                ],className="flex flex-col xl:grid xl:grid-cols-12 gap-6 p-2 m-2 flex-nowrap justify-around items-center"
            ),

],className="bg-gray-50 h-screen xl:fixed inset-0 ")


