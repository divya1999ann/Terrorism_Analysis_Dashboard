import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from app import App,region_graph
from homepage import Homepage
import pandas as pd
from scipy.interpolate import interp1d
import webbrowser
from threading import Timer


#loading dataset
data = pd.read_csv('terror-data1.csv')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED,'/assets/style.css'])

app.config.suppress_callback_exceptions = True




days_cnt= {30:[4,6,9,11],31:[1,3,5,7,8,10,12],29:[2]}


#filtering country according to region
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



#filtering cities according to country
cit={}
for i in data['country'].unique():
    li=[]
    x = data[data["country"]==i].index
    for j in range(len(x)):
        if data["city"][x[j]] not in li:
            li.append(data["city"][x[j]])
    cit[data["country_txt"][x[0]]] = li

app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])



#for routing
@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/chart-plots':
        return App()
    else:
        return Homepage()





#returning rows from dataset according to input
def lats(input1, input2, input3,input4,input5,input6):
    if input3!='ALL' and input4!='ALL' and input5!='ALL' and input6!='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['attacktype1_txt']==input3) & (data['region_txt']==input4) & (data['country_txt']==input5) & (data['city']==input6) ]
    elif input3!='ALL' and input4!='ALL' and input5!='ALL' and input6=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['attacktype1_txt']==input3) & (data['region_txt']==input4) & (data['country_txt']==input5) ]
    elif input3!='ALL' and input4!='ALL' and input5=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['attacktype1_txt']==input3) & (data['region_txt']==input4) ]
    elif input3!='ALL' and input4=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['attacktype1_txt']==input3) ]
    elif input3=='ALL' and input4=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) ]
    elif input3=='ALL' and input4!='ALL' and input5=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['region_txt']==input4)]
    elif input3=='ALL' and input4!='ALL' and input5!='ALL' and input6=='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2) & (data['region_txt']==input4) & (data['country_txt']==input5) ]
    elif input3=='ALL' and input4!='ALL' and input5!='ALL' and input6!='ALL':
        result = data[ (data['imonth']==input1) & (data['iday']==input2)  & (data['region_txt']==input4) & (data['country_txt']==input5) & (data['city']==input6)]
    print(result['latitude'])
    return result

#returning latitudes for second map
def lats1(inp1,inp2,inp3,inp4):
    data1 = data[data['country_txt']=='India']
    if inp3=='ALL':
        res= data1[ (data1['imonth']==inp1) & (data1['iday']==inp2) & (data1['provstate']==inp4) ]
    else:
        res= data1[ (data1['imonth']==inp1) & (data1['iday']==inp2) & (data1['attacktype1_txt']==inp3) & (data1['provstate']==inp4) ]
    return res



#------------------------------------------starting callbacks-------------------------------------------------------------



#callback for 'number of terrorist attacks country-wise' barplot
@app.callback(Output(component_id='region-bar',component_property='figure'),
[Input('reg-wise-count','value')])
def regwisecount(input_choice):
    graph = region_graph(input_choice)
    return graph


#callback for filtering days according to month
@app.callback(Output(component_id='day',component_property='options'),
[Input('mont','value')])
def makedays(input_choice):
    day_list = []
    c=0
    for j in days_cnt:
        if input_choice in days_cnt[j]:
            c = j
            break

    day_list =[ {'label':x , 'value': x} for x in range(1,c+1)]
    return day_list



#callback for filtering days according to month for second map
@app.callback(Output(component_id='day1',component_property='options'),
[Input('mont1','value')])
def makedays(input_choice):
    day_list = []
    c=0
    for j in days_cnt:
        if input_choice in days_cnt[j]:
            c = j
            break

    day_list =[ {'label':x , 'value': x} for x in range(1,c+1)]
    return day_list



#callback for filtering coutry according to region
@app.callback(Output(component_id='country',component_property='options'),
[Input('reg','value')])
def makecountry(input_choice):
    country_list = []
    c=0
    for j in d:
        if input_choice == j:
            country_list = d[j]
            break

    cnt_list =[ {'label':x , 'value': x} for x in country_list]
    cnt_list.append({'label':'ALL','value':'ALL'})
    return cnt_list



#callback for filtering city according to country
@app.callback(Output(component_id='city',component_property='options'),
[Input('country','value')])
def makecity(input_choice):
    city_list = []
    c=0
    for j in cit:
        if input_choice == j:
            city_list = cit[j]
            break

    cities_list =[ {'label':x , 'value': x} for x in city_list]
    cities_list.append({'label':'ALL','value':'ALL'})
    return cities_list



#callback for generating map 1
@app.callback(
    [
    Output(component_id='simple_graph', component_property='figure'),
     Output(component_id='concen_graph', component_property='figure')],
    [Input('bt1', 'n_clicks')],
    state=[State('mont', 'value'),
     State('day', 'value'),
     State('attacks', 'value'),
     State('reg', 'value'),
     State('country', 'value'),
     State('city', 'value'),
     ])
def compute(n_clicks, input1, input2, input3,input4,input5,input6):
    print(1)
    res = lats(input1, input2, input3,input4,input5,input6)
    fig = px.scatter_mapbox(res, lat="latitude", lon="longitude", hover_name="city",hover_data=['provstate','country_txt','region_txt','attacktype1_txt','iday','imonth','iyear'], labels={'provstate':'State','country_txt':'Country','region_txt':'Region','iday':'Day','imonth':'Month','iyear':'Year','attacktype1_txt':'Attack Type'} ,color='attacktype1', zoom=4 ,height=900)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig1=px.density_mapbox(res,lat="latitude", lon="longitude",hover_name="city",hover_data=['provstate','country_txt','region_txt','attacktype1_txt','iday','imonth','iyear'], labels={'provstate':'State','country_txt':'Country','region_txt':'Region','iday':'Day','imonth':'Month','iyear':'Year','attacktype1_txt':'Attack Type'},zoom=3,mapbox_style='open-street-map',height=400)
    return (fig,fig1)




#callback for generating map 2
@app.callback(Output(component_id='india_graph', component_property='figure'),
    [Input('bt2', 'n_clicks')],
    state=[State('mont1', 'value'),
     State('day1', 'value'),
     State('attacks1', 'value'),
     State('state_options', 'value')
     ])
def compute1(n_clicks, inp1, inp2, inp3,inp4):
    print(1)
    res1 = lats1(inp1, inp2, inp3,inp4)
    data1 = data[data['country_txt']=='India']
    state_cnt_list = []
    for i in data1['provstate'].unique():
        state_cnt_list.append(data['provstate'].value_counts()[i])
    m= interp1d([1,max(state_cnt_list)],[5,18])
    circle_radius = m(state_cnt_list)
    fig1=px.density_mapbox(res1,lat="latitude", lon="longitude",hover_name="city",zoom=3,radius = circle_radius,mapbox_style='open-street-map',height=400)
    return (fig1)




#callback for pie chart - Type of Attacks and their percentage in each year(page 2)
@app.callback(Output(component_id='year_graph',component_property='figure'),
[Input('year-attack','value')])
def yeargraph(input_choice):
    df=data[data['iyear']==input_choice]
    year_attacks = []
    for i in df['attacktype1_txt'].unique():
        l=[]
        l.append(i)
        l.append(df['attacktype1_txt'].value_counts()[i])
        year_attacks.append(l)
    year_attack_df = pd.DataFrame(year_attacks,columns=['Attack Type','attack_cnt'])
    fig = px.pie(year_attack_df, values='attack_cnt', names='Attack Type',
             title='Type of Attacks and their percentage in each year',
             hover_data=['attack_cnt'], labels={'attack_cnt':'Count'})
    return fig



#callback for pie chart - Type of Attacks and their percentage in each state(page 2)
@app.callback(Output(component_id='state_attack_type_pie',component_property='figure'),
[Input('state_attack_type','value')])
def yeargraph(input_choice):
    df = data[data['country_txt']=='India']
    state_att_type=[]
    dx = df[df['provstate']==input_choice]
    for i in dx['attacktype1_txt'].unique():
        l=[]
        l.append(i)
        l.append(dx['attacktype1_txt'].value_counts()[i])
        state_att_type.append(l)
    state_att_type_df = pd.DataFrame(state_att_type,columns=['Attack Type','Attack_cnt'])
    fig = px.pie(state_att_type_df, values='Attack_cnt', names='Attack Type',
             title='Type of Attacks and their percentage in each state',
             hover_data=['Attack_cnt'], labels={'Attack_cnt':'Count'})
    return fig




#callback for stack chart
@app.callback(Output(component_id='country_wise_line',component_property='figure'),
[Input('stacked_chart','value')])
def func_stacked_chart(input_choice):
    region_chart_list = []

    if input_choice==0:
        for i in data['iyear'].unique():
            dfx = data[data['iyear']==i]
            for j in dfx['region_txt'].unique():
                dfx1 = dfx[dfx['region_txt']==j]
                for k in dfx1['country_txt'].unique():
                    l=[]
                    l.append(i)
                    l.append(j)
                    l.append(k)
                    l.append(dfx1['country_txt'].value_counts()[k])
                    region_chart_list.append(l)
        region_chart_df = pd.DataFrame(region_chart_list,columns=['Year','Region','Country','Attack_cnt'])
        fig = px.area(region_chart_df, x="Year", y="Attack_cnt", color="Region",line_group="Country")

    elif input_choice==1:
        for i in data['iyear'].unique():
            dfx = data[data['iyear']==i]
            for j in dfx['region_txt'].unique():
                dfx1 = dfx[dfx['region_txt']==j]
                for k in dfx1['attacktype1_txt'].unique():
                    l=[]
                    l.append(i)
                    l.append(j)
                    l.append(k)
                    l.append(dfx1['attacktype1_txt'].value_counts()[k])
                    region_chart_list.append(l)
        region_chart_df = pd.DataFrame(region_chart_list,columns=['Year','Region','Attack_type','Attack_cnt'])
        fig = px.area(region_chart_df, x="Year", y="Attack_cnt", color="Region",line_group="Attack_type")

    elif input_choice==2:
        for i in data['iyear'].unique():
            dfx = data[data['iyear']==i]
            for j in dfx['region_txt'].unique():
                dfx1 = dfx[dfx['region_txt']==j]
                for k in dfx1['targtype1_txt'].unique():
                    l=[]
                    l.append(i)
                    l.append(j)
                    l.append(k)
                    l.append(dfx1['targtype1_txt'].value_counts()[k])
                    region_chart_list.append(l)
        region_chart_df = pd.DataFrame(region_chart_list,columns=['Year','Region','Target_type','Attack_cnt'])
        fig = px.area(region_chart_df, x="Year", y="Attack_cnt", color="Region",line_group="Target_type")

    elif input_choice==3:
        for i in data['iyear'].unique():
            dfx = data[data['iyear']==i]
            for j in dfx['region_txt'].unique():
                dfx1 = dfx[dfx['region_txt']==j]
                for k in dfx1['weaptype1_txt'].unique():
                    l=[]
                    l.append(i)
                    l.append(j)
                    l.append(k)
                    l.append(dfx1['weaptype1_txt'].value_counts()[k])
                    region_chart_list.append(l)
        region_chart_df = pd.DataFrame(region_chart_list,columns=['Year','Region','Weapon_type','Attack_cnt'])
        fig = px.area(region_chart_df, x="Year", y="Attack_cnt", color="Region",line_group="Weapon_type")

    return fig



#-----------------------------------------------------ending callbacks-------------------------------------------------------

def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')



if __name__ == '__main__':
	logging.basicConfig(filename="test.log",level=logging.DEBUG, format='%(asctime)s : %(levelname)s : %(message)s')
    webbrowser.open_new_tab('http://127.0.0.1:8050/') #for opening automatically
    app.run_server(debug=False)
