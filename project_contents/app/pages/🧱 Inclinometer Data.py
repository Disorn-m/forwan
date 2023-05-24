import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import random


st.set_page_config(layout="wide")

st.header('🧱 Inclinometer Data')
st.markdown("Inclinometers are used to obtain pile curvature readings using the beam bending equation over the various levels of lateral pile deformation (deflections, bending moments, shear). This tool was prepared by Fabien Blanchais. For more information about the tool and utilisation, see https://github.com/mottmacdonaldglobal/")


col1, col2 = st.columns(2)
project = col1.selectbox('Select Project',('Template', 'N101', 'N102', 'N105', 'N106', 'N107'), key='project')
instru_type = col2.selectbox('Select Instrument Type',('Template', 'IW', 'IS', 'IE'))

uploaded_files = st.file_uploader("Upload Masterlist & TEMS data",accept_multiple_files=True)
button = st.button("Read data")

if button and uploaded_files is not None:
        df=pd.DataFrame()
        for uploaded_file in uploaded_files:
            if uploaded_file.name == "I+M Tool_Instruments Masterlist.xlsx":
                nsc=pd.read_excel(uploaded_file,sheet_name=project)
                zones=nsc['Zone'].unique().tolist()
                
            elif uploaded_file.name == "Template.xlsx":
                df=pd.read_excel(uploaded_file,skiprows=1)
                # df=df.rename(columns={"taken_on": "(dd/mm/yyyy)"}) 
                # df=df.rename(columns={"Calculated Displacement A  (mm)": "at A (mm)"})
                # df=df.rename(columns={"INSTRUMENT ID": "Unnamed: 4"}) 
                # df=df.rename(columns={"instr_id": "(m)"}) 
                # for i, r in df.iterrows():
                #     depth=r["(m)"].split("-")
                #     depth=depth[-1]
                #     depth=depth.replace('m','')
                #     df.loc[i,"(m)"] = depth
                # df["(m)"]=df["(m)"].astype(float)
                
            else:
                d1=pd.read_excel(uploaded_file,sheet_name="IS",skiprows=4)
                d2=pd.read_excel(uploaded_file,sheet_name="IW",skiprows=4)
                d3=pd.read_excel(uploaded_file,sheet_name="IE",skiprows=4)

                d=pd.concat((d1, d2, d3), axis = 0)
                df=pd.concat((df, d), axis = 0)

        df["(dd/mm/yyyy)"] = pd.to_datetime(df["(dd/mm/yyyy)"]) # assigning column as timestamp format
        df["(dd/mm/yyyy)"] = df["(dd/mm/yyyy)"].dt.date # converting timestamp to datetime format
        df = df.groupby(by=["Unnamed: 4","(m)","(dd/mm/yyyy)"]).mean()
        df=df.reset_index()
        df=df.dropna(subset=['at A (mm)'])
        df=df.drop_duplicates()                
            
        st.session_state['df'] = df
        st.session_state['nsc'] = nsc
        st.session_state['zones'] = zones 

st.markdown("""---""")
if 'df' in st.session_state:
    
    df=st.session_state['df']
    nsc=st.session_state['nsc']
    zones=st.session_state['zones']
    
    col1, col2, col3, col4 = st.columns(4)
    
    zone_select = col1.selectbox('Zone', zones)
    
    instru_list=nsc[(nsc['Zone']==zone_select)]
    instru_list=instru_list.iloc[:]['Instrument ID'].tolist()
    instru_select = col2.selectbox('Instru ID', instru_list)
    
    ei=nsc[(nsc['Instrument ID']==instru_select)]
    ei_value=ei.iloc[0]['EI (kNm2)']
    ei_select = col3.number_input('EI (kNm2)', ei_value)

    reduced_lvl=ei.iloc[0]['Instrument Reduced Level (mSHD)']
    alert_lvl=ei.iloc[0]['Alert Level (mm)']
    worksuspension_lvl=ei.iloc[0]['Work Suspension Level (mm)']
    
    
    df=df[(df['Unnamed: 4']==instru_select)]
    min_date = df.iloc[:]['(dd/mm/yyyy)'].min()
    max_date = df.iloc[:]['(dd/mm/yyyy)'].max()
    date = col4.date_input('Date', (min_date, max_date))
    
    if project=='N101':
        col5, col6, col7 = st.columns(3)
        meth = col5.selectbox('Smoothing',("Gaussian","Moving average","Quadratic"))
        wind = col6.slider(label='Select smoothing window', min_value=0, max_value=10, value=2)
        predet_lvl=col7.number_input('Insert PDL (mm)',value=10)
   
    else:    
        col5, col6 = st.columns(2)
        meth = col5.selectbox('Smoothing',("Gaussian","Moving average","Quadratic"))
        wind = col6.slider(label='Select smoothing window', min_value=0, max_value=10, value=2)

    
    fig = make_subplots(rows=2, cols=3, vertical_spacing = 0.05, shared_yaxes=True)
    df = df[(df["(dd/mm/yyyy)"]>=date[0]) & (df["(dd/mm/yyyy)"]<=date[1])]
    date_list=df['(dd/mm/yyyy)'].unique().tolist()
    


    n=0
    for date in date_list:
            
        color= "%06x" % random.randint(1, 0xFFFFFF)
        
        df_date=df[(df['(dd/mm/yyyy)']==date)]
        df_date=df_date.dropna(subset=['at A (mm)'])
        df_date=df_date.sort_values(by='(m)', ascending=True)
        
        #TODO when do data
       
        df_date['dz'] = df_date['(m)'].diff() 
        df_date['dy'] = df_date['at A (mm)'].diff()
        df_date['dy'] = df_date['dy']/1000
        df_date['slope'] = df_date['dy']/df_date['dz']
        df_date['dslope']= df_date['slope'].diff()
        df_date['moment'] = (ei_value*df_date['dslope'])/df_date['dz']
        df_date['dmoment']= df_date['moment'].diff()
        df_date['shear']= df_date['dmoment']/df_date['dz']
        df_date['(m)'] = reduced_lvl-df_date['(m)']
        df_date=df_date.dropna(subset=['shear'])
        df_date=df_date.reset_index()
        
        if n==0:
            df_date['AL1']=alert_lvl
            df_date['WSL1']=worksuspension_lvl
            df_date['AL2']=alert_lvl*-1
            df_date['WSL2']=worksuspension_lvl*-1
            fig.add_trace(go.Scatter(x=df_date['AL1'], y=df_date['(m)'], showlegend=True, name='AL', line=dict(color="#0614AE",dash='dash',width=2)))
            fig.add_trace(go.Scatter(x=df_date['AL2'], y=df_date['(m)'], showlegend=False, line=dict(color="#0614AE",dash='dash',width=2)))
            fig.add_trace(go.Scatter(x=df_date['WSL1'], y=df_date['(m)'], showlegend=True, name='WSL', line=dict(color="#d90404",dash='dash',width=3)))
            fig.add_trace(go.Scatter(x=df_date['WSL2'], y=df_date['(m)'], showlegend=False, line=dict(color="#d90404",dash='dash',width=3)))
            
            if project=='N101':
                df_date['PDL1']=predet_lvl
                df_date['PDL2']=predet_lvl*-1
                fig.add_trace(go.Scatter(x=df_date['PDL1'], y=df_date['(m)'], showlegend=True, name='PDL', line=dict(color="#ba22f4",dash='dash',width=2)))
                fig.add_trace(go.Scatter(x=df_date['PDL2'], y=df_date['(m)'], showlegend=False, line=dict(color="#ba22f4",dash='dash',width=2)))

               
        if meth=="Quadratic":
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='lines+markers',marker=dict(color='grey',size=3)),row=1, col=1)
            
            df_date['mnb']= (df_date.index / wind + 1).astype(int)                
            df_date = df_date[['mnb','(m)','at A (mm)','moment','shear']]
            df_date=df_date.groupby(by=["mnb"]).mean().reset_index()
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
            fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
            fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
        n=n+1
        
        if meth=="Moving average":
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='lines+markers',marker=dict(color='grey',size=3)),row=1, col=1)
            
            df_date= df_date[['(m)','at A (mm)','moment','shear']].rolling(wind).mean()      
            df_date=df_date.dropna()
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
            fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
            fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
        n=n+1
        
        if meth=="Gaussian":
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"),mode='lines+markers',marker=dict(color='grey',size=3)),row=1, col=1)

            df_date= df_date[['(m)','at A (mm)','moment','shear']].rolling(window=wind,win_type='gaussian').mean(std=7)      
            df_date=df_date.dropna()
            fig.add_trace(go.Scatter(x=df_date['at A (mm)'], y=df_date['(m)'], legendgroup=n, showlegend=True, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=1)
            fig.add_trace(go.Scatter(x=df_date['moment'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=2)
            fig.add_trace(go.Scatter(x=df_date['shear'], y=df_date['(m)'], legendgroup=n, showlegend=False, name=date.strftime("%d/%m/%Y"), line=dict(color="#"+color),line_shape='spline'),row=1, col=3)
        n=n+1


    mmcol1, mmcol2, mmcol3, mmcol4, mmcol5, mmcol6, mmcol7 = st.columns(7)
    moment_minmax = mmcol4.slider('Moment x-axis range', value=[-10000,10000],key='moment_minmax_key')
    shear_minmax = mmcol6.slider('Shear x-axis range', value=[-10000,10000],key='shear_minmax_key')
    
    
    

    st.download_button('Download data', df.to_csv(), file_name="Data.csv")
    fig.update_traces(mode='lines')
    fig.update_layout(autosize=False, width=1100, height=1700, xaxis1_title = 'Deflection (mm)', xaxis2_title = 'Moment (kN-m)', xaxis3_title = 'Shear(kN)',yaxis1_title='Level (mSHD)',
                      xaxis2_range=[moment_minmax[0],moment_minmax[1]],xaxis3_range=[shear_minmax[0],shear_minmax[1]])
    # fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    