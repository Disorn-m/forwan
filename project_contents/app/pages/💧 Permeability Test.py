# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 09:44:36 2023

@author: LIM105592
@author: BLA88076
"""

import streamlit as st
from plotly.subplots import make_subplots
import math
import pandas as pd
import plotly.graph_objects as go
import numpy as np


st.set_page_config(layout="wide")

st.header('💧 Permeability Test')
st.markdown("Interpretation of permeability test results using the variable head method (BS 22282-2). This tool was prepared by Fabien Blanchais and Lim Chin Seng. For more information about the tool and utilisation, see https://github.com/mottmacdonaldglobal/")

#PART ONE: DEFINING THE WIDGETS
#Upload section
uploaded =  st.file_uploader("Upload file here",type=('xlsx','csv'),accept_multiple_files=False)
ok_upload = st.button("Read Data",key='uploader')

#Output after the upload OK button is clicked

if ok_upload:
    if uploaded is not None:    
        #st.success("Your file has been successfully uploaded! \n")
        st.session_state.key='df'
        try:
            st.session_state['df']= pd.read_excel(uploaded)
        except:
            st.session_state['df']= pd.read_csv(uploaded)
        
        st.session_state.key='file uploaded'
        st.session_state['file uploaded']='file uploaded'

    else:
        st.error('Your file cannot be found, please try again \n')

#Method choice dropdown widget for analysis method
if 'df' in st.session_state:
    col1,col2=st.columns([1,1])
    method_variable_head = "Variable Head"
    method_constant_rate = '\u0336' + '\u0336'.join("Constant Rate")
    method_constant_head = '\u0336' + '\u0336'.join("Constant Head")
    method_options = col1.selectbox("Choose Test",options=("-",method_variable_head, method_constant_rate, method_constant_head))

    vh_velocity_graph = "Velocity Graph"
    vh_hvorslev = '\u0336' + '\u0336'.join("Hvorslev")
    vh_cbp = '\u0336' + '\u0336'.join("Cooper-Bredehoeft-Papadopoulos")
    vh_options = col2.selectbox('Choose Method', options=['-', vh_velocity_graph, vh_hvorslev, vh_cbp])
    
    #Water level and well geometry
    col3,col4,col5 = st.columns([1,1,1])
    water_level = col3.number_input('Original Water Level (mbgl):', step=0.01,disabled=False,key='water')
    pipe_length = col4.number_input('Well Length (m):',step=0.01, disabled=False,key='length')
    pipe_dm = col5.number_input('Well Diameter (m):',step=0.001, disabled=False,key='dm')
    
    if vh_options==vh_velocity_graph and method_options==method_variable_head:
        st.session_state.key='method done'
        st.session_state['method done']='done'

#Section for subsetting graph
if 'method done' in st.session_state:
    #Getting data from local session state
    perm_df                       = st.session_state['df']
    perm_df["Head (m)"]           = abs(water_level - perm_df["Depth (m)"])
    perm_df["Head Ratio, Ht/Ho"]  = perm_df["Head (m)"] / perm_df["Head (m)"][0]
    perm_df["ln(Ho/Ht)"]          = np.log(1/perm_df["Head Ratio, Ht/Ho"])
        
    time_log_list = perm_df["Time (min)"].values.tolist()
    selected_time_begin = []
    selected_time_end   = []
    
        
    st.markdown("\nEnter the **Start Time and End Time (min) for analysis**:")
    col6,col7 = st.columns([1,1])
    selected_time_begin.append(col6.selectbox('Start:',options= time_log_list,key="Box1"))
    selected_time_end.append(col7.selectbox('End:',options= time_log_list,key="Box2"))
            
    
    #Plots the points of the data, use blue as color for individual points
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=perm_df["Time (min)"], y=perm_df["ln(Ho/Ht)"], mode = 'markers',
                             showlegend=True, name='Logarithmic Head Ratio against Time', line=dict(color="blue")))
          
    #Generating graph subsection lines after selecting time
    #Code creates list with [start_time_1,end_time_1,......,start_time_n,end_time_n]
    final_list = [item for sublist in zip(selected_time_begin, selected_time_end) for item in sublist]
    gradient_list = []
    weight_k      = []
    
    
    if len(final_list)==2 and final_list[0] == 0 and final_list[1] == 0:
        gradient_list = [0]
        weight_k      = [0]
        pass
    
    else:
        st.markdown("Data shown below is the dataset with the slope of the subset")
        base_color = ['green', 'red', 'orange', 'blue', "yellow"]
        n = math.ceil(6/len(base_color))
        color_list = n * base_color
        
        for i in range(len(final_list)):

            if i%2 == 0:

                shown_data = perm_df[(perm_df["Time (min)"]>=final_list[i]) & (perm_df["Time (min)"]<=final_list[i+1])]
                x = shown_data["Time (min)"]
                y = shown_data["ln(Ho/Ht)"]

                #use green as color for individual points
                m, b  = np.polyfit(x, y, 1)

                perm_df["Regression Line"] = m*x + b
                fig.add_trace(go.Scatter(x=perm_df["Time (min)"], y=perm_df["Regression Line"], showlegend=True, name='Subset Line', line=dict(color=color_list[int(i/2)])))
                gradient_list.append(m)
                weight_k.append(len(shown_data["Time (min)"])/(len(perm_df["Time (min)"])+1))

            else:
                pass
    fig.update_layout(autosize=False, width=250, height=500,xaxis_title = 'Time (min)',yaxis_title = 'ln(Ho/Ht)')
    st.plotly_chart(fig, use_container_width=True)        
        
    st.session_state.key='gradient_list'
    st.session_state['gradient_list']=gradient_list
    st.session_state.key='weight_k'
    st.session_state['weight_k']=weight_k
    

    #PART THREE: RESULTS
    st.markdown("""---""")
    st.markdown("**Results**")
    #Calculation of L/D ratio
    L = pipe_length
    D = pipe_dm
    area    = np.pi * (D/2)**2
    st.session_state.key = 'area'
    st.session_state['area'] = area

    #Shows the L/D ratio
    ratio_ld      = L / D
    ratio_string = str(round(ratio_ld, 2))
    
    if ratio_ld > 10:
        
        #Calculation of intake factor (F)
        F = 2*np.pi*L / (np.log(2*L/D))
        F_string = str(round(F, 2))
        
        
        st.markdown("Based on the input parameters, the length to diameter ratio (L/D) of the well is %s" %ratio_string +
                    ". According to the BN EN ISO 22282-1:2012 standard, the formula for the intake factor (F) when L/D > 10 can be seen in Equation 1." +
                    " Using this formula, the calculated intake factor (F) is %s" %F_string +
                    '. The formula for the Velocity Graph method can be seen in equation 2 below. Based on this formula, the permeability (k) for the dataset is') 
        
        col8,col9,col10 = st.columns([1,1,1])
        col11,col12,col13 = st.columns([1,1,1])
        col11.latex(r''' (Eq. 1) \space F =\frac {2 \pi L}{ln(2 \cdot \frac {L}{D})} -(1) ''')
        
        
    elif 1.2 < ratio_ld <= 10:
        F = 2*np.pi*L / (np.log(ratio_ld + np.sqrt(ratio_ld**2 + 1)))
        F_string = str(round(F, 2))
        st.markdown("Based on the input parameters, the length to diameter ratio (L/D) of the well is %s" %ratio_string +
                    ". According to the BN EN ISO 22282-1:2012 standard, the formula for the intake factor (F) when 1.2 < L/D < 10 can be seen in Equation 1. " +
                    " Using this formula, the calculated intake factor (F) is %s"%F_string + 
                    '. The formula for the Velocity Graph method can be seen in equation 2 below. Based on this formula, the permeability (k) for the dataset is') 
        
        col8,col9,col10 = st.columns([1,1,1])
        col11,col12,col13 = st.columns([1,1,1]) 
        col11.latex(r''' (Eq. 1) \space F =\frac {2 \pi L}{ln((\frac {L}{D}) + \sqrt {((\frac{L}{D})^2 + 1)})} -(1) ''')
        
    #Velocity graph formula
    col13.latex(r''' (Eq. 2) \space k = \frac {A} {F (t_2 - t_1)} ln(\frac{H_1}{H_2}) -(2) ''')

    #Calculation of the permeability values
    if gradient_list == [0]:
        col9.latex(r'0 m/s')
                    
    else:
        #Calculation of permeability (for the whole dataset)
        k = area * gradient_list[0] / (F * 60)

        #Converting into string to be put in the button widget
        perm = str(k)
        tenthpower = str(-int(perm[-1]))   
        decimal     = perm[:5]
        col9.latex(rf'''k = {decimal} \times 10^{tenthpower} \space \space m/s''')
                
 
    



