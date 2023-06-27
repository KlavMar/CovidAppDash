# #import libraries
# from os import name
# from dash import Dash,html,dcc,Input,Output
# import plotly.graph_objs as go
# from django_plotly_dash import DjangoDash
# import pandas as pd
# from portfolio.base.graph import *
# from portfolio.base.default_config import *
# from app.src.covid.app_dash.app_dash_standard import *
# from app.src.connection_db import ConnectionDb
# import os 
# from dotenv import load_dotenv
# from dotenv import dotenv_values
# from math import *
# from sqlalchemy import text
# load_dotenv()
# config = dotenv_values(".env")


# dir_app=Path(__file__).resolve().parent

# path=f'{dir_app}/{dir_csv}/'


# password = os.getenv("mdp_connection_covid")
# user = os.getenv("user_name_covid")
# host = os.getenv("host")
# port = os.getenv("port")
# db = os.getenv("database_covid")

# con=ConnectionDb(host,port,user,password,db)
# db_connection=con.get_connection()
# # contamination sourcing 

# app = DjangoDash(name ='covid_per_country',external_stylesheets=external_stylesheets)

# sql = text("""SELECT date_reported AS date,CONCAT(MONTHNAME(date_reported),'-',YEAR(date_reported)) AS date_concat,
#     country,new_cases,new_deaths,cumulative_cases,cumulative_deaths 
#     FROM covid_daily
#     WHERE date_reported = (SELECT max(date_reported) FROM covid_daily)
#     """)
# df = pd.read_sql_query(sql,db_connection)

# def get_graph(df,ma,col,name):
#     if ma != None:
#         df[f'ma_{col}_{ma}']=df[col].rolling(ma).mean()
#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(
#         x=df["date"],y=df[col],name=name,marker_color="#0ea5e9",line=dict(width=3)
#         )
#     )
#     try:
#         fig.add_trace(
#             go.Scatter(
#             x=df["date"],y=df[f"ma_{col}_{ma}"],name=f"moyenne mobile {ma} jours",marker_color="#dc2626",line=dict(width=3)
#             )
#         )
#     except:
#         pass
#     get_templates(fig)
#     return fig 

# def mask(country):
#     df = pd.read_sql_query(sql,db_connection)
#     df["date"] = pd.to_datetime(df["date"],format="%Y-%m-%d")
#     mask = ((df.country == country))

#     df_graph = df.loc[mask, :]
#     return df_graph




# @app.callback(Output('country_select', 'children'),[Input('country','value')])
# def get_country(country):
#     return country


# @app.callback(Output('last_cases', 'children'),[Input('country','value')])
# def get_number_last_day(country):
#     df_graph=mask(country)
#     df_graph = df_graph.sort_values(by="date",ascending=False)

#     last_cases_number = df_graph.new_cases.to_list()
#     last_death_number=df_graph.new_deaths.to_list()
#     style={"width":"45vw","background":"#f0f9ff","color":"#525252","display":"flex","flex-flow":"column","font-size":"1.25em","padding":"1em","margin":"0.5em","font-weight":"600","border":"0.25em solid #0284c7","border-radius":"0.5em"}
#     return html.Div(
#         children=[

#          html.Div(children=[
#         html.H2("Données J-1"),
#          html.P(f"Contamination {last_cases_number[0]}"),
#         html.P(f"Décès {last_death_number[0]}")
#         ],style=style)
        
#         ,        
#         html.Div(children=[
#          html.H2("Données J-7"),
#          html.P(f"Contamination {last_cases_number[6]}"),
#         html.P(f"Décès {last_death_number[6]}")
#         ],style=style)
#         ],style={"display":"flex","flex-flow":"row","justify-content":"space-around","padding":"3em"})

# @app.callback(Output('new_cases','figure'),[Input('country','value'), Input("ma", "value")])
# def get_contamination(country,ma=None):

#     df_graph = mask(country)
#     fig = get_graph(df_graph,ma,"new_cases","Nouvelles contaminations")
#     fig.update_layout(title="Historique des contaminations")
#     return fig

# @app.callback(Output('new_death','figure'),[Input('country','value'), Input("ma", "value")])
# def get_death(country,ma=None):
#     df_graph = mask(country)
#     fig = get_graph(df_graph,ma,"new_deaths","Nouveaux décès")
#     fig.update_layout(title="Historique des décès")
#     return fig

# @app.callback(Output("cumulative_cases","figure"),[Input('country','value')])
# def get_cumulative_cases(country,ma=None):
#     df_graph=mask(country)
#     fig = get_graph(df_graph,ma,"cumulative_cases","Sommes des contaminations")
#     fig.update_layout(title="Contaminations totale")
#     return fig 

# @app.callback(Output("cumulative_deaths","figure"),[Input('country','value')])
# def get_cumulative_deaths(country,ma=None):
#     df_graph=mask(country)
#     fig = get_graph(df_graph,ma,"cumulative_deaths","Total décès")
#     fig.update_layout(title="Total dècès")
#     return fig 







# app.layout=html.Div([
#     html.Div([
#         html.Div(
#     children=[
       
#        html.Div(
#                 children = [
#                         html.H3(children="Pays", style={"color":"black"}),
#                         dcc.Dropdown(
#                             id="country",options =[{'label':i, 'value':i } for i in sorted(df.country.unique())],
#                             value="France",
#                             className="dropdown-item"
#                         )
#                     ],className="container-dropdown-filter",style={"display":"flex","flex-flow":"row","color":"black","align-items":"center","justify-content":"space-between"}
#                 ),
#         html.Div(
#                 children=[
#                     html.H3(children="Moyenne mobile", style={"color":"black"}),
#                     dcc.Dropdown(
#                         id="ma",options =[{'label':i, 'value':i } for i in range(0,60,10)],
#                         value=10,className="dropdown-item"
#                     )
#                     ],className="container-dropdown-filter",style={"display":"flex","flex-flow":"row","color":"black","align-items":"center","justify-content":"space-between"}
#                 ),
#     ],style={"display":"flex","flex-flow":"row","color":"black","align-items":"center","justify-content":"center"}
#         ),
#         html.H1(id='country_select', children=[],style={"margin":"0.75em auto","padding":"0.5em","font-weight":"700","color":"#111827"}),
#         html.Div(id="last_cases",children=[]),
#         html.Div(
#             children=[
#             dcc.Graph(id="new_cases",className="container-graph",style=style_graph),
#             dcc.Graph(id="new_death",className="container-graph",style=style_graph),
    
#             ],className="block-container-graph"
            
#         ),
#         html.Div(
#             children=[
#                 dcc.Graph(id="cumulative_cases",className="container-graph",style=style_graph),
#                 dcc.Graph(id="cumulative_deaths",className="container-graph",style=style_graph),
#             ],className="block-container-graph"
#         )
#     ],style={"width":"95vw","height":"95vh","margin":"auto"})
# ], style={"margin":"1em auto","padding":"0.5em"})


