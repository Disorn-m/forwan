import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import random


st.set_page_config(layout="wide")

st.header('🧱 Inclinometer Data')
st.markdown("Inclinometers are used to obtain pile curvature readings using the beam bending equation over the various levels of lateral pile deformation (deflections, bending moments, shear). This tool was prepared by Fabien Blanchais. For more information about the tool and utilisation, see https://github.com/mottmacdonaldglobal/")

uploaded_files = st.file_uploader("",accept_multiple_files=True)
option = st.selectbox('Select Instrument Type',('IW', 'IS', 'IE'))
button = st.button("Read data")

def form_callback():
    st.session_state['callback'] = True

if button and uploaded_files is not None:
    if option =="IS"or"IW"or"IE":
        df=pd.DataFrame()
        for uploaded_file in uploaded_files:
            d1=pd.read_excel(uploaded_file,sheet_name="IS",skiprows=4)
            d2=pd.read_excel(uploaded_file,sheet_name="IW",skiprows=4)
            d3=pd.read_excel(uploaded_file,sheet_name="IE",skiprows=4)
            
            d=pd.concat((d1, d2, d3), axis = 0)
            df=pd.concat((df, d), axis = 0)
            df["(dd/mm/yyyy)"] = pd.to_datetime(df["(dd/mm/yyyy)"]) # assigning column as timestamp format
            df["(dd/mm/yyyy)"] = df["(dd/mm/yyyy)"].dt.date # converting timestamp to datetime format
            df=df.dropna(subset=['at A (mm)'])
            df=df[df['Unnamed: 4'].str.contains(option, na=False)]
            
        df=df.drop_duplicates()
        min_date = df.iloc[:]['(dd/mm/yyyy)'].min()
        max_date = df.iloc[:]['(dd/mm/yyyy)'].max()
        instruments=df['Unnamed: 4'].unique().tolist()
        
        st.session_state['df'] = df
        st.session_state['instruments'] = instruments
        
        with st.form(key='my_form'):
            col1, col2, col3, col4 = st.columns(4)
            date = col1.date_input('Date', (min_date, max_date),key='date')
            inst = col2.selectbox('Instrument',instruments,key='inst')
            meth = col3.selectbox('Smoothing',("Gaussian","Moving average","Quadratic"),key='meth')
            ei = col4.number_input('EI',key='ei')
            
            st.slider(label='Select smoothing window', min_value=0, max_value=10, value=7, key='wind')
            
            submitted = st.form_submit_button('Show plots',on_click=form_callback) 


try:
    
    if 'callback' in st.session_state:
        
        with st.form(key='my_form'):
            
            col1, col2, col3, col4 = st.columns(4)
            date = col1.date_input('Date', (st.session_state['date'][0], st.session_state['date'][1]),key='date')
            inst = col2.selectbox('Instrument',st.session_state['instruments'],key='inst')
            meth = col3.selectbox('Smoothing',("Gaussian","Moving average","Quadratic"),key='meth')
            ei = col4.number_input('EI',key='ei')
            
            st.slider(label='Select smoothing window', min_value=0, max_value=10, value=7, key='wind')
            
            submitted = st.form_submit_button('Show plots',on_click=form_callback)       
            
            fig = make_subplots(rows=2, cols=3, vertical_spacing = 0.05)
            df=st.session_state['df']
            df=df[(df['Unnamed: 4']==st.session_state['inst'])]
            
            df = df[(df["(dd/mm/yyyy)"]>=st.session_state['date'][0]) & (df["(dd/mm/yyyy)"]<=st.session_state['date'][1])]
            date_list=df['(dd/mm/yyyy)'].unique().tolist()
            
            n=0
            for date in date_list:
                color= "%06x" % random.randint(1, 0xFFFFFF)
                
                df_date=df[(df['(dd/mm/yyyy)']==date)]
                df_date=df_date.dropna(subset=['at A (mm)'])
                df_date=df_date.sort_values(by='(m)', ascending=True)
                
                df_date['dz'] = df_date['(m)'].diff()
                df_date['dy'] = df_date['at A (mm)'].diff()
                df_date['slope'] = df_date['dy']/df_date['dz']
                df_date['dslope']= df_date['slope'].diff()
                df_date['moment'] = (st.session_state['ei']*df_date['dslope'])/df_date['dz']
                df_date['dmoment']= df_date['moment'].diff()
                df_date['shear']= df_date['dmoment']/df_date['dz']
                df_date=df_date.dropna(subset=['shear'])
                df_date=df_date.reset_index()

                
                if st.session_state['meth']=="Quadratic":
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=2)
                    fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=3)
                    
                    df_date['mnb']= (df_date.index / st.session_state['wind'] + 1).astype(int)                
                    df_date = df_date[['mnb','(m)','at A (mm)','moment','shear']]
                    df_date=df_date.groupby(by=["mnb"]).mean().reset_index()
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
                    fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
                n=n+1
                
                if st.session_state['meth']=="Moving average":
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=2)
                    fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),line=dict(color='grey'),line_shape='spline'),row=1, col=3)
                    
                    df_date= df_date[['(m)','at A (mm)','moment','shear']].rolling(st.session_state['wind']).mean()      
                    df_date=df_date.dropna()
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
                    fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
                n=n+1
                
                if st.session_state['meth']=="Gaussian":
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='lines+markers',marker=dict(color='grey',size=3)),row=1, col=1)
                    #fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='markers',marker=dict(color='grey')),row=1, col=2)
                    #fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='markers',marker=dict(color='grey')),row=1, col=3)

                    df_date= df_date[['(m)','at A (mm)','moment','shear']].rolling(window=st.session_state['wind'],win_type='gaussian').mean(std=7)      
                    df_date=df_date.dropna()
                    fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
                    fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
                    fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
                n=n+1

            #fig.update_traces(mode='lines')
            #fig.update_layout(title_text=st.session_state['inst'])
            fig.update_layout(autosize=False, width=1100, height=1700, xaxis1_title = 'Deflection (mm)', xaxis2_title = 'Moment (kN-m)', xaxis3_title = 'Shear(kN)',yaxis1_title='Depth (m)')
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig)
        
except Exception:
    pass