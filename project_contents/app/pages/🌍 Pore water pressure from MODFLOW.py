# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 21:16:31 2023

@author: BLA88076
"""

import streamlit as st
from zipfile import ZipFile 
import flopy.utils.binaryfile as bf
import numpy as np
import flopy
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default='png'

#Before running code, remember to create config.toml via notepad and paste following inside:
#[server]
#maxUploadSize=10000

st.set_page_config(layout="wide")

st.header('🌍 Pore water pressure from MODFLOW')
st.markdown('Pore water pressure profiles and top elevation of geological layers from MODFLOW are generated at row and column inputs (i,j). Upload a zip folder containing .hed and .dis files. This tool was prepared by Fabien Blanchais. For more information about the tool and utilisation, see https://github.com/mottmacdonaldglobal/')

doe = st.file_uploader('Upload .dis and .hed file', type = '.zip', accept_multiple_files= False)

if (doe is not None):
    zf = ZipFile(doe)
    for item in zf.namelist():
        if item.endswith('.hed'):
            file = zf.extract(item, 'hds_file')
            hds = bf.HeadFile(file)
            head = hds.get_data(totim=None)
                
        if item.endswith('.dis'):
            file = zf.extract(item, 'dis_file')
            m = flopy.modflow.Modflow()
            dis = flopy.modflow.ModflowDis.load(file, m)
            bot = m.dis.getbotm()
            top = m.dis.gettop()
    
    st.markdown('Select i, j ,k values')
    col1,col2,col3 = st.columns([1,1,1])
    i = col1.number_input('Value of i', value = 1)
    j = col2.number_input('Value of j', value = 1)
    
    #number of layers to display based on layer number in bot
    layernb = col3.number_input('Bottom layer', max_value = bot.shape[0], key = 'layernb') 
        
       
    elev_list=[]
    head_list=[]
    top_list=[]
            
    for layer in np.arange(0,len(head)):
        if layer == 0:
            mid_elev = (top + bot[layer,:,:])/2
            top_list.append(top[i,j])
        else:
            mid_elev=(bot[layer-1,:,:] + bot[layer,:,:])/2
            top_list.append(bot[layer-1,i,j])
                
        if layer != layernb:
            head_list.append(head[layer,i,j])
            elev_list.append(mid_elev[i,j])
                
    df = pd.DataFrame(elev_list,columns=["elev"])
    df["head"] = pd.DataFrame(head_list,columns=["head"])
    df["top"] = pd.DataFrame(top_list,columns=["top"])
    df["pressure_head_m"] = df["head"]-df["elev"]
    df["pressure_head_kPa"] = df["pressure_head_m"]*9.81
            
    for i,r in df.iterrows():
        if r["pressure_head_kPa"] < 0:
            df.loc[i,"pressure_head_kPa"] = 0
            
    fig = make_subplots(rows = 1, cols = 1)
    fig.add_trace(go.Scatter(x = df['pressure_head_kPa'], y = df['elev'], showlegend = True, name = 'Pore Water Pressure', line = dict(color = "#0614AE", dash = 'dash',width = 2)))
    
    max_pwp=df["pressure_head_kPa"].max()   
    for r in np.arange(0,len(df)):
        if r==0:
            fig.add_trace(go.Scatter(x = [0, max_pwp * 4 / 3],y = [df.iloc[r]['top'],df.iloc[r]['top']], name = 'Top Elevation', mode = 'lines', showlegend = True, line = dict(color = "#808080")))
        else:
            fig.add_trace(go.Scatter(x = [0, max_pwp * 4 / 3],y = [df.iloc[r]['top'],df.iloc[r]['top']], mode = 'lines', showlegend = False, line = dict(color = "#808080")))
    
    fig.update_layout(xaxis_title = 'Pore Water Pressure (kPa)', yaxis_title = 'Elevation (mASL)')
    st.plotly_chart(fig , use_container_width = True)          
            
    