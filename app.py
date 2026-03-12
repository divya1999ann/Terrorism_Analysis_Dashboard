import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from navbar import Navbar
import plotly.graph_objects as go
import numpy as np
import gc

# ─── MEMORY-OPTIMIZED DATA LOADING ────────────────────────────────────────────
# Only load the columns you actually use.
# `nkill` and `nwound` are optional because some dataset exports omit them.
REQUIRED_COLS = [
    'iyear', 'region_txt', 'country_txt', 'provstate',
    'attacktype1_txt', 'targtype1_txt'
]
OPTIONAL_COLS = ['nkill', 'nwound']
DATA_URL = 'https://terror-data-bucket.s3.eu-north-1.amazonaws.com/terror-data1.csv'

available_cols = pd.read_csv(DATA_URL, nrows=0).columns.tolist()
missing_required = [c for c in REQUIRED_COLS if c not in available_cols]
if missing_required:
    raise ValueError(f"Dataset is missing required columns: {missing_required}")

cols_to_load = [c for c in REQUIRED_COLS + OPTIONAL_COLS if c in available_cols]
data = pd.read_csv(DATA_URL, usecols=cols_to_load, low_memory=True)

# Convert string columns to 'category' dtype — saves ~60% RAM on these columns
for col in ['region_txt', 'country_txt', 'provstate', 'attacktype1_txt', 'targtype1_txt']:
    data[col] = data[col].astype('category')

# Downcast numeric columns
data['iyear'] = pd.to_numeric(data['iyear'], errors='coerce').astype('Int16')
if 'nkill' in data.columns:
    data['nkill'] = pd.to_numeric(data['nkill'], errors='coerce').astype('float32')
else:
    data['nkill'] = np.nan
    data['nkill'] = data['nkill'].astype('float32')

if 'nwound' in data.columns:
    data['nwound'] = pd.to_numeric(data['nwound'], errors='coerce').astype('float32')
else:
    data['nwound'] = np.nan
    data['nwound'] = data['nwound'].astype('float32')

# ─── PRE-COMPUTE AGGREGATES ONCE ──────────────────────────────────────────────
# This replaces all the slow value_counts() loops in each function.
# We compute summary tables once and discard nothing (the full data is still
# needed for filtered views), but aggregates are tiny compared to the raw data.

reg_counts    = data['region_txt'].value_counts().reset_index()
reg_counts.columns = ['region_name', 'region_cnt']

year_counts   = data['iyear'].value_counts().reset_index()
year_counts.columns = ['Year', 'year_cnt']

attack_counts = data['attacktype1_txt'].value_counts().reset_index()
attack_counts.columns = ['Attack_type', 'Attack_cnt']

target_counts = data['targtype1_txt'].value_counts().reset_index()
target_counts.columns = ['Target_type', 'Attack_cnt']

india_data    = data[data['country_txt'] == 'India'].copy()

state_counts  = india_data['provstate'].value_counts().reset_index()
state_counts.columns = ['State', 'Attack_cnt']

india_attacks = india_data['attacktype1_txt'].value_counts().reset_index()
india_attacks.columns = ['Attack Type', 'attack_cnt']

india_year_counts = india_data['iyear'].value_counts().reset_index()
india_year_counts.columns = ['Year', 'Attack_cnt']
# Fill in years with 0 attacks
all_years = pd.DataFrame({'Year': range(1970, 2019)})
india_year_counts = all_years.merge(india_year_counts, on='Year', how='left').fillna(0)
india_year_counts = india_year_counts.sort_values('Year')

# Force garbage collection after setup
gc.collect()

nav = Navbar()

# ─── CHART FUNCTIONS (now use pre-computed aggregates — no loops) ──────────────

def reg_count():
    return px.bar(reg_counts, x='region_name', y='region_cnt',
                  labels={'region_cnt': 'Number of Attacks', 'region_name': 'Region'},
                  color='region_cnt', title='Number of terrorist attacks region-wise', height=500)

def year_count():
    return px.bar(year_counts.sort_values('Year'), x='Year', y='year_cnt',
                  labels={'year_cnt': 'Number of Attacks', 'Year': 'Year'},
                  color='year_cnt', title='Number of terrorist attacks year-wise', height=500)

def attack_count():
    return px.bar(attack_counts, x='Attack_type', y='Attack_cnt',
                  labels={'Attack_cnt': 'Number of Attacks', 'Attack_type': 'Attack Types'},
                  color='Attack_cnt', title='Number of terrorist attacks attack-type-wise', height=500)

def state_count():
    return px.bar(state_counts, x='State', y='Attack_cnt',
                  labels={'Attack_cnt': 'Number of Attacks', 'State': 'State'},
                  color='Attack_cnt', title='State-wise Attack Concentration in India', height=500)

def attacks_count():
    return px.pie(india_attacks, values='attack_cnt', names='Attack Type',
                  title='Type of Attacks in India and their percentage',
                  hover_data=['attack_cnt'], labels={'attack_cnt': 'Count of attacks'})

def india_count():
    return px.line(india_year_counts, x='Year', y='Attack_cnt',
                   labels={'Attack_cnt': 'Number of Attacks'},
                   title='Year Wise attack count in India')

def india_attack_year():
    # Most common attack type per year in India
    year_attack_type = (
        india_data.groupby(['iyear', 'attacktype1_txt'])
        .size()
        .reset_index(name='cnt')
    )
    # Keep only the top attack type per year
    idx = year_attack_type.groupby('iyear')['cnt'].idxmax()
    top = year_attack_type.loc[idx].rename(columns={'iyear': 'Year', 'attacktype1_txt': 'Attack Type'})
    return px.scatter(top.sort_values('Year'), x='Year', y='Attack Type')

def ind_attacktype():
    year_att_type = (
        india_data.groupby(['iyear', 'attacktype1_txt'])
        .size()
        .reset_index(name='Attack_cnt')
    )
    year_att_type.columns = ['Year', 'Attack Type', 'Attack_cnt']
    return px.scatter(year_att_type, x='Year', y='Attack Type', color='Attack Type',
                      size='Attack_cnt', hover_data=['Attack Type', 'Attack_cnt'],
                      labels={'Attack_cnt': 'Attack Count'})

def targettype_count():
    return px.pie(target_counts, values='Attack_cnt', names='Target_type',
                  title='Target types and their percentage',
                  hover_data=['Attack_cnt'],
                  labels={'Attack_cnt': 'Count of attacks', 'Target_type': 'Target Type'})

def con_regwise():
    rc = reg_counts['region_cnt'].values[:12]
    r = rc.reshape(3, 4)
    fig = px.imshow(r, color_continuous_scale=px.colors.sequential.Cividis_r,
                    title="Concentration of attacks in various regions")
    annotations = [
        "Middle East & North Africa", "South Asia", "Sub-Saharan Africa", "South America",
        "Western Europe", "Southeast Asia", "Central America & Caribbean", "Eastern Europe",
        "North America", "East Asia", "Central Asia", "Australasia & Oceania"
    ]
    positions = [(i, j) for i in range(3) for j in range(4)]
    for ann, (row, col) in zip(annotations, positions):
        fig.add_annotation(x=col, y=row, text=ann, showarrow=False,
                           font=dict(size=8, color='white'), xref='x', yref='y')
    return fig

def func_state_type():
    return dcc.Dropdown(
        id='state_attack_type',
        options=[{'label': i, 'value': i} for i in sorted(india_data['provstate'].dropna().unique())],
        placeholder='Select a state'
    )

def func_stacked_chart():
    return dcc.Dropdown(
        id='stacked_chart',
        options=[
            {'label': 'By country',     'value': 0},
            {'label': 'By Attack Type', 'value': 1},
            {'label': 'By target type', 'value': 2},
            {'label': 'By weapon type', 'value': 3},
        ],
        value=0
    )

def region_graph(input_choice):
    df = data[data['region_txt'] == input_choice]
    reg_df = df['country_txt'].value_counts().reset_index()
    reg_df.columns = ['country_name', 'country_cnt']
    return px.bar(reg_df, x='country_name', y='country_cnt',
                  labels={'country_cnt': 'Number of Attacks', 'country_name': 'Country'},
                  title='Number of terrorist attacks country-wise (in each region)', height=500)

# ─── LAYOUT ───────────────────────────────────────────────────────────────────

def App():
    layout = html.Div([
        nav,
        html.Div(
            style={'backgroundColor': '#D3D3D3'},
            children=[
                html.Br(), html.Br(),
                html.H1("Infographics - Global Analysis",
                        style={'textAlign': 'center', 'color': '#456fBv'}),
                html.Br(),
            ]
        ),
        html.Br(), html.Br(),
        html.H5('Choose a region'),
        dcc.Dropdown(
            id='reg-wise-count',
            options=[{'label': i, 'value': i} for i in sorted(data['region_txt'].dropna().unique())],
            placeholder="Please select a region",
        ),
        dcc.Graph(id='region-bar'),
        html.Br(),
        dcc.Graph(id='region-count',   figure=reg_count()),
        html.Br(),
        dcc.Graph(id='year-count',     figure=year_count()),
        html.Br(),
        dcc.Graph(id='attack-count',   figure=attack_count()),
        html.Br(),
        dcc.Graph(id='con-region',     figure=con_regwise()),
        html.Br(),
        html.P("Choose a year"),
        dcc.Dropdown(
            id='year-attack',
            options=[{'label': i, 'value': i} for i in sorted(data['iyear'].dropna().unique())],
            placeholder="Please select a year"
        ),
        dcc.Graph(id='year_graph'),
        html.Br(),
        html.P('Incidents per year grouped by'),
        html.Div([func_stacked_chart()]),
        dcc.Graph(id='country_wise_line'),
        html.Br(),
        dcc.Graph(id='target_type',    figure=targettype_count()),
        html.Br(),
        html.Div(style={'backgroundColor': '#000000'}, children=[html.Br()]),
        html.Div(
            style={'backgroundColor': '#D3D3D3'},
            children=[
                html.Br(),
                html.H2('India Infographics', style={'textAlign': 'center', 'color': '#456fBv'}),
                html.Br()
            ]
        ),
        html.Br(), html.Br(),
        dcc.Graph(id='state_wise',            figure=state_count()),
        html.Br(),
        dcc.Graph(id='india_attacks',         figure=attacks_count()),
        html.Br(),
        html.P('Choose a state'),
        html.Div([func_state_type()]),
        dcc.Graph(id='state_attack_type_pie'),
        html.Br(),
        dcc.Graph(id='india-yearwise',        figure=india_count()),
        html.Br(),
        dcc.Graph(id='india-attacktype-yearwise', figure=india_attack_year()),
        html.Br(),
        dcc.Graph(id='ind-year-attacktype',   figure=ind_attacktype()),
    ])
    return layout