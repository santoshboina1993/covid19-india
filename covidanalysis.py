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

from PIL import Image
logo_main = Image.open('./title.png')

def main():
    st.markdown("""
        <style>
        body {
            color: #262730;
            background-color: #ffffff	;
            etc. 
                }

            </style>
            """, unsafe_allow_html=True)

    st.markdown('''<style> 
                h2{color: #000080;}
                </style>''', unsafe_allow_html=True)
    

    url='https://www.mohfw.gov.in/'

    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, "lxml")
    htmltable = soup.find_all('table')
 
    def tableDataText(table):       
        rows = []
        trs = table.find_all('tr')
        headerow = [td.get_text(strip=True) for td in trs[0].find_all('th')] # header row
        if headerow: # if there is a header row include first
            rows.append(headerow)
            trs = trs[1:]
    
        for tr in trs: # for every table row
            rows.append([td.get_text(strip=True) for td in tr.find_all('td')]) # data row
        return rows

    list_table = tableDataText(htmltable[1])
    dftable = pd.DataFrame(list_table[1:],columns=list_table[0])
    dftable1 = dftable[:-1]
    #------------------------------------------------------------------------------------------------------
    trs1 = htmltable[0].find_all('tr')
    rows1 = []
    for tr in trs1: # for every table row
        rows1.append([td.get_text(strip=True) for td in tr.find_all('td')])
 
    dftable_event = pd.DataFrame(rows1[2:],columns = ['Date','Title'])  
    dftable_event.set_index('Date', inplace=True)   
    #--------------------------------------------------------------------------------------------------------
    dftable1[['Total Confirmed cases (Indian National)','Total Confirmed cases ( Foreign National )','Death','Cured/Discharged/Migrated']] =     dftable1[['Total Confirmed cases (Indian National)','Total Confirmed cases ( Foreign National )','Death','Cured/Discharged/Migrated']].apply(pd.to_numeric) 

    dftable1['total'] = dftable1['Total Confirmed cases (Indian National)'] + dftable1['Total Confirmed cases ( Foreign National )']+ dftable1['Death'] + dftable1['Cured/Discharged/Migrated']
    dftable1 = dftable1.sort_values(by='total',ascending = False)
    sumvals = pd.DataFrame(dftable[-1:])


    st.image(logo_main,use_column_width=True)
 
    confirmed_cases_indian = sumvals.iloc[0]["Name of State / UT"]
    confirmed_cases_foreign = sumvals.iloc[0]["Total Confirmed cases (Indian National)"]
    total_death = sumvals.iloc[0]["Cured/Discharged/Migrated"]
    total_cured = sumvals.iloc[0]["Total Confirmed cases ( Foreign National )"]
    
    st.markdown('<h2><strong>Confirmed cases in India</strong></h2>',unsafe_allow_html = True)
    from datetime import date
    st.write("as on date:",date.today())
     

        
    eval_matrix = [['Indian Nationals','Foreign Nationals', 'Deaths'],
               [f'<b>{confirmed_cases_indian}</b>',f'<b>{confirmed_cases_foreign}</b>', f'<b>{total_death}</b>']]

    table = ff.create_table(eval_matrix,height_constant = 50)
        
    for i in range(len(table.layout.annotations)):
        table.layout.annotations[i].font.size = 20
      
            
    st.plotly_chart(table)
    st.markdown('---')
    st.markdown('<h2><strong>Latest Updates</strong></h2>',unsafe_allow_html = True)
    st.write(dftable_event)
    st.markdown('---')
    
    def cases_statewise(dftable1):
        trace1 = go.Bar(x=dftable1['Name of State / UT'], y=dftable1["Total Confirmed cases (Indian National)"],name = "Indian Nationals",marker=dict(color='#000080'))
        trace2 = go.Bar(x=dftable1['Name of State / UT'], y=dftable1["Total Confirmed cases ( Foreign National )"],name = "Foreign Nationals")
        
        data = [trace1,trace2]
        layout = go.Layout(
        barmode= 'stack',    
        xaxis=dict(title='States /UT'),
        yaxis=dict(title='Count'),
        bargap=0.1,
        bargroupgap=0.1,
        template= 'plotly_white',
        width= 950
        
        )
        fig = go.Figure(data=data, layout=layout)
        return(fig)

    st.markdown('<h2><strong>Indian/Foreigners Count by States</strong></h2>',unsafe_allow_html = True)
    sel = st.slider("Most affected states:",min_value=3,max_value= 22,value = 5)
    st.plotly_chart(cases_statewise(dftable1[:sel]))
                    
    st.markdown('---')
    st.markdown('<h2><strong>State level Death/Cure Analysis</strong></h2>',unsafe_allow_html = True)
    df_transposed = dftable1.T
    #df_transposed.columns = df_transposed.index[1]
    df_transposed = df_transposed.drop(df_transposed.index[0])
    headers = df_transposed.iloc[0]
    new_df  = pd.DataFrame(df_transposed.values[1:], columns=headers)
    st.subheader("Select s State:")
    state_slcted = st.selectbox(" ",list(new_df.columns),index = 7)
    labels = ['Cures','Death']
    values = list(new_df[state_slcted])
    values = values[2:4]
    if sum(values)>0:
        fig = go.Figure(data=[go.Pie(labels=labels,values=values)])
        st.plotly_chart(fig)
    else:
        st.subheader("There are no deaths/cures for selected state")
    st.markdown('---')

    st.subheader('Resources:')   
    
    st.markdown('''
    - Data: [mohfw.gov.in] (https://www.mohfw.gov.in/)
    - Developed By: [Santosh Boina] (https://www.linkedin.com/in/santoshboina/)
    ''')    
       
if __name__ == "__main__":
    main()
