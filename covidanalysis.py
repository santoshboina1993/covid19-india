import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import numpy as np
import requests
import lxml.html as lh
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.figure_factory as ff
import json
from pandas.io.json import json_normalize
from plotly.subplots import make_subplots
from datetime import date
    
url_datewise='https://api.rootnet.in/covid19-in/stats/history'
#url_total="https://api.rootnet.in/covid19-in/stats/latest"

json_content = requests.get(url_datewise).text
data = json.loads(json_content)
grouped_data  = (json_normalize(data['data'],record_path=['regional'],meta = ['day']))
grouped_data['day'] = grouped_data['day'].astype('datetime64[ns]') 

def line_plot(state_name,filter_df):
    trace_1 = go.Scatter(x=filter_df['day'], y=filter_df['totalConfirmed'],
                    mode='lines',
                    name='Confirmed Cases')
    trace_2 = go.Scatter(x=filter_df['day'], y=filter_df['deaths'],
                    mode='lines',
                    name='Deaths')
    trace_3 = go.Scatter(x=filter_df['day'], y=filter_df['discharged'],
                    mode='lines',
                    name='Cured')
    data = [trace_1,trace_2,trace_3]
    
    layout = go.Layout(
    xaxis=dict(title='Date'),
    yaxis=dict(title='Count'),
    template= 'plotly_white',
    width= 900
    )
    fig = go.Figure(data=data, layout=layout)
    
    return (fig)
    
def present_stats(present_confirmed,present_death,present_discharged):
    
    table_data = [['      Confirmed', '         Deaths', '      Discharged'],
                [ f'           <b>{present_confirmed}</b>', f'            <b>{present_death}</b>', f'          <b>{present_discharged}</b>']]

    colorscale = [[0, '#ffffff'],[.5, '#000000'],[1, '#ffffff']]
    font=['#000000']
    
    fig = ff.create_table(table_data, colorscale=colorscale,font_colors=font)

    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 20

    return (fig)

def overall_count(total_confirmed,total_deaths,total_discharged):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
    mode = "number",
    value = total_confirmed,
    title = 'Confirmed',
    domain = {'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(
    mode = "number",
    value = total_deaths,
    title='Deaths',
    domain = {'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
    mode = "number",
    value = total_discharged,
    title='Discharged',
    domain = {'row': 0, 'column': 2}))

    
    fig.update_layout(
    grid = {'rows': 2, 'columns': 3, 'pattern': "independent"},
    height = 600,
    font = {'color': "darkblue"}
    )
    return fig



if __name__ =='__main__':
    st.title("COVID-19 India Dashboard")
    st.write('as on date ',date.today())
    total_data = grouped_data.groupby(['loc']).last()

    total_confirmed = sum(total_data['totalConfirmed'])
    total_deaths = sum(total_data['deaths'])
    total_discharged = sum(total_data['discharged'])

    st.plotly_chart(present_stats(total_confirmed,total_deaths,total_discharged))

    trace1 = go.Bar(x=total_data.index, y=total_data["discharged"],name = "Discharged",marker=dict(color='#8FBC8F'))
    trace2 = go.Bar(x=total_data.index, y=total_data["deaths"],name = "Deaths",marker=dict(color='#8B0000'))
    trace3 = go.Scatter(x=total_data.index,y=total_data['totalConfirmed'],name = "Total Confirmed",marker=dict(color='#d3d3d3 '),fill='tozeroy',mode='lines',opacity=0.7)
    
    data = [trace3,trace1,trace2]
    layout = go.Layout(
        barmode= 'stack',    
        xaxis=dict(title='States /UT'),
        yaxis=dict(title='Count'),
        bargap=0.1,
        bargroupgap=0.1,
        template= 'plotly_white',
        width= 950,
        height=600
    
        )
    fig = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig)
    
    selected_state = st.selectbox("State",list(set(grouped_data['loc'])))
    filter_df = grouped_data[grouped_data['loc']==selected_state]
    present_df = filter_df.tail(1)
    present_confirmed=present_df.iloc[0]['totalConfirmed']
    present_death = present_df.iloc[0]['deaths']
    present_date = present_df.iloc[0]['day']
    present_discharged = present_df.iloc[0]['discharged']
    #st.markdown(f'<h3><strong>COVID cases in India as on {date.today()}</strong></h3>',unsafe_allow_html = True)
    st.write(f"In {selected_state} ,as on date:",date.today())
    st.plotly_chart(present_stats(present_confirmed,present_death,present_discharged))
    
    st.plotly_chart(line_plot(selected_state,filter_df))
    
