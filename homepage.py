import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import pandas as pd
import dash_html_components as html  #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px
import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from navbar import Navbar


nav = Navbar()


data = pd.read_csv('terror-data1.csv')



months = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
days_cnt= {30:[4,6,9,11],31:[1,3,5,7,8,10,12],29:[2]}
regions={}
d={}
for i in data['region'].unique():
    reg_c=[]
    x = data[data["region"]==i].index
    for j in range(len(x)):
        if data["country_txt"][x[j]] not in reg_c:
            reg_c.append(data["country_txt"][x[j]])
    d[data["region_txt"][x[0]]] = reg_c
    regions[i] = data["region_txt"][x[0]]


cit={}
for i in data['country'].unique():
    li=[]
    x = data[data["country"]==i].index
    for j in range(len(x)):
        if data["city"][x[j]] not in li:
            li.append(data["city"][x[j]])
    cit[data["country_txt"][x[0]]] = li





#----------------------------------------------------------starting functions------------------------------------------------------------------


#function for month dropdown for map1
def func_month():
    mon = data['imonth'].unique().tolist()
    l=[]
    mon.sort()
    for imon in mon:
        l.append({'label':months[imon],'value':imon})

    return dcc.Dropdown(
        id='mont',
        options= l,
         placeholder = 'Select a month'
       )


#function for month dropdown for map2
def func_month1():
    mon = data['imonth'].unique().tolist()
    l=[]
    mon.sort()
    for imon in mon:
        l.append({'label':months[imon],'value':imon})

    return dcc.Dropdown(
        id='mont1',
        options= l,
         placeholder = 'Select a month'
       )


#function for attack type dropdown for map1
def func_attacks():
    attack_list = data['attacktype1_txt'].unique().tolist()
    attacks_list = []
    for k in attack_list:
        attacks_list.append({'label':k,'value':k})
    attacks_list.append({'label':'ALL','value':'ALL'})

    return dcc.Dropdown(
        id='attacks',
        options=attacks_list ,
        placeholder = 'Select a attack type'
    )


#function for attack type dropdown for map2
def func_attacks1():
    attack_list = data['attacktype1_txt'].unique().tolist()
    attacks_list = []
    for k in attack_list:
        attacks_list.append({'label':k,'value':k})
    attacks_list.append({'label':'ALL','value':'ALL'})

    return dcc.Dropdown(
        id='attacks1',
        options=attacks_list ,
        placeholder = 'Select a attack type'
    )


#function for regions dropdown for map1
def func_regions():
    regions_li = data['region_txt'].unique().tolist()
    reg2 = []
    for k in regions_li:
        reg2.append({'label':k,'value':k})
    reg2.append({'label':'ALL','value':'ALL'})

    return dcc.Dropdown(
        id='reg',
        options= reg2,
        placeholder = 'Select a region'
    )


#function for state dropdown for map2
def func_state():
    df = data[data['country_txt']=='India']
    state = df['provstate'].unique().tolist()
    state_list = []
    for j in state:
        state_list.append({'label':j,'value':j})

    return dcc.Dropdown(
        id='state_options',
        options= state_list,
         placeholder = 'Select a state'
       )

#--------------------------------------------------ending functions-----------------------------------------------------------------

#layout for homepage

def Homepage():
    layout = html.Div([
    nav,
    html.Div(
        style={
        'backgroundColor':'#D3D3D3',
        },
        children=[ 
            html.Br(),
            html.Br(),
            html.H1(children = "Welcome to Terrorism Analysis Dashboard",
            style={
                'textAlign':'center',
                'color':'#456fBv',

            }
    ),
    html.Br(),
    ]
    ),

    html.Div( children = "Please select the required options",
            style={
                'textAlign':'center'
            }
    ),
    html.Br(),
    html.Div(id='d1',
    children=[html.Label("Choose a month"),
    html.Div([func_month()])]
    ),  
    html.Br(),
    html.Div(
    id='d2',
    children= [html.Label("Choose a day"),
    dcc.Dropdown(
        id='day',
        placeholder = 'Select a day'
    )]),
    

    html.Br(),
    html.Label("Choose a attack type"),
    html.Div([func_attacks()]),


    html.Br(),
    html.Label("Choose a region"),
    html.Div([func_regions()]),


    html.Br(),
    html.Label("Choose a country"),
    dcc.Dropdown(
        id='country',
        placeholder = 'Select a country'
    ),

    
    html.Br(),
    html.Label("Choose a city"),
    dcc.Dropdown(
        id='city',
        placeholder = 'Select a city'
    ),

    html.Br(),
    
    html.Div(
        style = {'textAlign':'center'},
        children=[html.Button('GENERATE GRAPH',id='bt1')]),


    html.Br(),
    html.Br(),

    html.Div(
        id='g1',
        children=[dcc.Graph(
        id= 'simple_graph',
    )]),
    html.Br(),
    html.H4(children='Heat Map',style={
        'textAlign':'center'
    }),
    dcc.Graph(
        id='concen_graph'
    ),

    html.Br(),


    html.Div(style={
        'backgroundColor': '#000000' 
    },
    children=[html.Br()]),
    html.Div(
        style={
        'backgroundColor':'#D3D3D3',
        },
        children=[
            html.Br(),
            html.H2(children='Indian Infographics',
                style={
                'textAlign':'center',
                'color':'#456fBv'
                }
        ),
        html.Br()
        ]
    ),
     html.Div(style={
        'backgroundColor': '#000000' 
    },
    children=[html.Br()]),

    html.Br(),
    html.Label("Choose a month"),
    html.Div([func_month1()]),

    html.Br(),
    html.Label("Choose a day"),
    dcc.Dropdown(
        id='day1',
        placeholder = 'Select a day'
    ),
    html.Br(),
    html.Label("Choose a attack type"),
    html.Div([func_attacks1()]),
    html.Br(),
    html.Label("Choose a state"),
    html.Div([func_state()]),
    html.Br(),
    html.Div(
        style = {'textAlign':'center'},
        children=[html.Button('GENERATE GRAPH',id='bt2')]),

    html.Br(),
    dcc.Graph(id='india_graph'),

    ])
    return layout




app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])

app.layout = Homepage()
