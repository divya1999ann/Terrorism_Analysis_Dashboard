import pandas as pd     #(version 1.0.0)
import plotly           #(version 4.5.0)
import plotly.express as px
import dash             #(version 1.8.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from navbar import Navbar
import plotly.graph_objects as go   
import numpy as np
import plotly.graph_objs as go



data = pd.read_csv('terror-data1.csv')

nav = Navbar()



#function for counting attacks region-wise
def reg_count():
    rlist = []
    for i in data['region_txt'].value_counts().index:
        l=[]
        l.append(i)
        l.append(data['region_txt'].value_counts()[i])
        rlist.append(l)
    r_df = pd.DataFrame(rlist,columns=['region_name','region_cnt'])
    fig = px.bar(r_df, x='region_name', y='region_cnt',labels={'region_cnt':'Number of Attacks','region_name':'Region'},color="region_cnt",title='Number of terrorist attacks region-wise',height=500)
    
    return fig



#function for counting attacks year-wise
def year_count():
    year_list = []
    for i in data['iyear'].value_counts().index:
        l=[]
        l.append(i)
        l.append(data['iyear'].value_counts()[i])
        year_list.append(l)
    year_df = pd.DataFrame(year_list,columns=['Year','year_cnt'])
    fig = px.bar(year_df, x='Year', y='year_cnt',labels={'year_cnt':'Number of Attacks','Year':'Year'},color="year_cnt", title='Number of terrorist attacks year-wise', height=500)
    return fig



#function for attacks attack type wise
def attack_count():
    attack_type_list = []
    for i in data['attacktype1_txt'].unique():
        l=[]
        l.append(i)
        l.append(data['attacktype1_txt'].value_counts()[i])
        attack_type_list.append(l)
    attack_type_df = pd.DataFrame(attack_type_list,columns=['Attack_type','Attack_cnt'])
    fig = px.bar(attack_type_df, x='Attack_type', y='Attack_cnt',labels={'Attack_cnt':'Number of Attacks','Attack_type':'Attack Types'},color="Attack_cnt",title='Number of terrorist attacks attack-type-wise', height=500)
    return fig




#function for counting attacks state-wise and returning bar plot
def state_count():
    df = data[data['country_txt']=='India']
    state_list = []
    for i in df['provstate'].unique():
        l=[]
        l.append(i)
        l.append(df['provstate'].value_counts()[i])
        state_list.append(l)
    state_df = pd.DataFrame(state_list,columns=['State','Attack_cnt'])
    fig = px.bar(state_df, x='State', y='Attack_cnt',labels={'Attack_cnt':'Number of Attacks','State':'State'},color="Attack_cnt",title='State-wise Attack Concentration in India', height=500)
    return fig




#function for counting attacktypes in india and returning pie chart
def attacks_count():
    df = data[data['country_txt']=='India']
    india_attacks = []
    for i in df['attacktype1_txt'].unique():
        l=[]
        l.append(i)
        l.append(df['attacktype1_txt'].value_counts()[i])
        india_attacks.append(l)
    india_attack_df = pd.DataFrame(india_attacks,columns=['Attack Type','attack_cnt'])
    fig = px.pie(india_attack_df, values='attack_cnt', names='Attack Type',
             title='Type of Attacks in India and their percentage',
             hover_data=['attack_cnt'], labels={'attack_cnt':'Count of attacks'})
    return fig




#function for line plot of year v/s number of attacks
def india_count():
    df = data[data['country_txt']=='India']
    india_cnt_list = []
    for i in df['iyear'].unique():
        l=[]
        l.append(i)
        l.append(df['iyear'].value_counts()[i])
        india_cnt_list.append(l)
    d=[]
    for i in range(1970,2019):
        if i not in df['iyear'].unique():
            d.append(i)
    for i in d:
        l=[]
        l.append(i)
        l.append(0)
        india_cnt_list.append(l)
    india_cnt_list.sort()
    india_cnt_df = pd.DataFrame(india_cnt_list,columns=['Year','Attack_cnt'])
    fig = px.line(india_cnt_df, x="Year", y="Attack_cnt",labels={'Attack_cnt':'Number of Attacks'}, title='Year Wise attack count in India')
    return fig



#scatter plot for attack type v/s year
def india_attack_year():
    df = data[data['country_txt']=='India']
    year_attack_type=[]
    for i in df['iyear'].unique():
        dx = df[df['iyear']==i]
        m = max(dx['attacktype1_txt'].value_counts())
        for j in dx['attacktype1_txt'].unique():
            l=[]
            if dx['attacktype1_txt'].value_counts()[j] == m:
                l.append(i)
                l.append(j)
                year_attack_type.append(l)
    year_attack_type.sort()
    india_year_df = pd.DataFrame(year_attack_type,columns=['Year','Attack Type'])
    fig = px.scatter(india_year_df,x='Year', y='Attack Type')
    return fig



#scatter plot for year v/s attack type
def ind_attacktype():
    df = data[data['country_txt']=='India']
    year_att_type=[]
    for i in df['iyear'].unique():
        dx = df[df['iyear']==i]
        for j in dx['attacktype1_txt'].unique():
            l=[]
            l.append(i)
            l.append(j)
            l.append(dx['attacktype1_txt'].value_counts()[j])
            year_att_type.append(l)
    india_type_df = pd.DataFrame(year_att_type,columns=['Year','Attack Type','Attack_cnt'])
    fig = px.scatter(india_type_df, x="Year", y="Attack Type", color="Attack Type",size='Attack_cnt', hover_data=['Attack Type','Attack_cnt'],labels={'Attack_cnt':'Attack Count'})
    return fig




#function for dropdown state-wise attack type
def func_state_type():
    df = data[data['country_txt']=='India']
    l=[]
    for i in df['provstate'].unique():
        l.append({'label':i,'value':i})
    return dcc.Dropdown(
        id='state_attack_type',
        options= l,
         placeholder = 'Select a state'
       )




#function for heatmap
rlist = []
for i in data['region_txt'].value_counts().index:
    l=[]
    l.append(i)
    l.append(data['region_txt'].value_counts()[i])
    rlist.append(l)
r_df = pd.DataFrame(rlist,columns=['region_name','region_cnt'])
def con_regwise():
    rc = r_df['region_cnt']
    r = np.array(rc)
    r = r.reshape(3,4)
    t = r_df['region_name']
    t = np.array(t)
    fig = px.imshow(r, color_continuous_scale=px.colors.sequential.Cividis_r,title="Concentration of attacks in various regions")
    fig.add_annotation(
    x=0.42,
    y=0.9,
    text="Middle East & North Africa",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.47,
    y=0.9,
    text="South Asia",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.53,
    y=0.9,
    text="Sub-Saharan Africa",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.58,
    y=0.9,
    text="South America",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.42,
    y=0.5,
    text="Western Europe",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.47,
    y=0.5,
    text="Southeast Asia",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.53,
    y=0.5,
    text="Central America & Caribbean",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.58,
    y=0.5,
    text="Eastern Europe",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.42,
    y=0.17,
    text="North America",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.47,
    y=0.17,
    text="East Asia",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.53,
    y=0.17,
    text="Central Asia",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),
    fig.add_annotation(
    x=0.58,
    y=0.17,
    text="Australasia & Oceania",
    xref="paper",
    yref="paper",
    showarrow=False,
    font_size=8, font_color='white'),


    return fig




#layout for App page(page 2)
def App():
    layout = html.Div([
    nav,
    html.Div(
        style={
        'backgroundColor':'#D3D3D3',
        },
        children=[ 
            html.Br(),
            html.Br(),
            html.H1(children = "Infographics - Global Analysis",
            style={
                'textAlign':'center',
                'color':'#456fBv',

            }
    ),
    html.Br(),
    ]
    ),
    html.Br(),
    html.Br(),
    html.H5('Choose a region'),
    dcc.Dropdown(
        id='reg-wise-count',
        options= [
          {'label': i , 'value': i} for i in data['region_txt'].unique()
        ],
        placeholder="Please select a region",
    ),
    dcc.Graph(id='region-bar'),

    html.Br(),
    dcc.Graph(id='region-count',figure=reg_count()),

    html.Br(),
    dcc.Graph(id='year-count',figure=year_count()),

    html.Br(),
    dcc.Graph(id='attack-count',figure=attack_count()),

    html.Br(),
    dcc.Graph(id='con-region',figure=con_regwise()),

    html.Br(),
    html.P("Choose a year"),
    dcc.Dropdown(id="year-attack",
    options =[
        {'label':i,'value':i} for i in data['iyear'].unique()
    ],
    placeholder="Please select a year"
    ),
    dcc.Graph(id="year_graph"),

    html.Br(),

    html.Div(style={
        'backgroundColor':'#D3D3D3',
        },
        children=[
            html.Br(),
            html.H2(children='India Infographics',
             style={
                'textAlign':'center',
                'color':'#456fBv',

            }),
            html.Br()
        ]
        ),
    html.Br(),
    html.Br(),
    dcc.Graph(id='state_wise',figure=state_count()),

    html.Br(),
    dcc.Graph(id='india_attacks',figure=attacks_count()),

    html.Br(),
    html.P('Choose a state'),
    html.Div([func_state_type()]),
    dcc.Graph(id='state_attack_type_pie'),

    html.Br(),
    dcc.Graph(id='india-yearwise', figure=india_count()),

    html.Br(),
    dcc.Graph(id='india-attacktype-yearwise',figure=india_attack_year()),

    html.Br(),
    dcc.Graph(id='ind-year-attacktype',figure=ind_attacktype())


    ])
    return layout



def region_graph(input_choice):
    df = data[data["region_txt"]==input_choice]
    reg_list=[]
    for i in df['country_txt'].unique():
        l=[]
        l.append(i)
        l.append(df['country_txt'].value_counts()[i])
        reg_list.append(l)
    reg_df = pd.DataFrame(reg_list,columns=['country_name','country_cnt'])
    fig = px.bar(reg_df, x='country_name', y='country_cnt',labels={'country_cnt':'Number of Attacks','country_name':'Country'}, title='Number of terrorist attacks country-wise (in each region)', height=500)
    return fig
