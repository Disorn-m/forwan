# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 09:44:36 2023

@author: LIM105592
@author: BLA88076
"""

from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from shapely.geometry import LineString
from datetime import timedelta
from scipy.spatial import distance

import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math
import streamlit as st



st.set_page_config(layout="wide")
st.header('⌛ Settlement Analysis')

 #to use colors, apply color[index%8] as % 8 gives back remainder and thus iterate through the values 0 to 7, if is 2 graph then is [index*2%8] amnd [(index*2+1)%8]
colors = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']

def files_to_df(data):
    df_list = []
    col_names=[]
    for i in range(len(data)):
        try:
            df_list.append(pd.read_excel(data[i]))
        except:
            df_list.append(pd.read_csv(data[i]))
            
    df_list = pd.concat(df_list).reset_index(drop=True).fillna(0) 
    col_names = df_list.columns.values.tolist()
    
    return df_list,col_names      
  
#Definitions used for plots            
def mini_maxi(df,col):
    mini=df[col].min()
    maxi=df[col].max()
    mini_d=df.index.min()
    maxi_d=df.index.max()
    return (mini, maxi, mini_d, maxi_d)

def min_max_in_tuples(tuple1,tuple2):
    mini=min(tuple1[0],tuple2[0])
    maxi=max(tuple1[1],tuple2[1])
    mini_d=min(tuple1[2],tuple2[2])
    maxi_d=max(tuple1[3],tuple2[3])
    return (mini, maxi, mini_d, maxi_d)

def settlement_plot(settled_df, constructed_df,settle_id, settle_data, construct_data, annotate_df = None): #annotate_df was previously **annotate_df which was wrong
    #settlement data dh plot
    fig = make_subplots(rows=2, cols=1, row_heights=[60,30], 
                        specs=[[{"secondary_y": True}],[{"secondary_y": False}]], shared_xaxes=True,vertical_spacing = 0.05)
    mini_maxi_dh = (math.inf,-math.inf,pd.Timestamp.max,pd.Timestamp.min)
    fig.add_trace(go.Scatter(x=constructed_df.index, y=constructed_df[construct_data],
                             name=constructed_df.iloc[0,0]),row=1, col=1, secondary_y=True)
    settle_list = list(set(settled_df[settle_id].tolist()))
    
    for id_dh in settle_list:
        df = settled_df.loc[settled_df[settle_id]==id_dh]
        df[settle_data] = df[settle_data].abs()
        df_daily = df.resample('D').max()
        df_daily = df_daily.interpolate('linear')
        df_daily['dh'] = df_daily[settle_data].diff()/df_daily.index.to_series().diff().dt.days # denom was previously df_daily.index.to_series().diff().astype('timedelta64[D]').astype('Int64')
        df_daily = df_daily.dropna()
        
        
        fig.add_trace(go.Scatter(x=df.index, y=df[settle_data],name=id_dh),row=1, col=1)
        fig.add_trace(go.Scatter(x=df_daily.index, y=df_daily['dh'],name=f"{id_dh}-dh"),row=2, col=1)
        mini_maxi_dh_loop = mini_maxi(df_daily,'dh')
        mini_maxi_dh = min_max_in_tuples(mini_maxi_dh, mini_maxi_dh_loop)

    
    mini_maxi_df = mini_maxi(settled_df,settle_data)
    mini_maxi_load = mini_maxi(constructed_df,construct_data)
    min_max_tuples = min_max_in_tuples(mini_maxi_df, mini_maxi_load)

    y_range = mini_maxi_df[1]-mini_maxi_df[0]
    y_add = (10*y_range)/100
            
    x_range = (min_max_tuples[3]-min_max_tuples[2]).days
    x_add = (2*x_range)/100
    x_add = timedelta(days=x_add)
    
    if annotate_df is not None:
        try:
            for index, row in annotate_df.iterrows():
                xs = row[0]
                xe = row[0]
                fig.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_df[0],mini_maxi_df[1]],name=row[1],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=1, col=1)
                fig.add_annotation(text=row[1], x=xs-x_add, y=mini_maxi_df[0]+y_add, showarrow=False,textangle=-90,opacity=0.5, font=dict(color="grey"))
                fig.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_dh[0],mini_maxi_dh[1]],name=row[1],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=2, col=1)
        except Exception as e:
            st.write(annotate_df)
            st.write(e)
            pass
            
    fig.update_layout(height=850, xaxis2_title = 'Time',yaxis1_title='Settlement (mm)', yaxis1_autorange="reversed", yaxis2_title="Construction height (m)", yaxis3_title="mm/day")
    st.plotly_chart(fig,use_container_width=True)
    
def piezo_plot(piezo_df, constructed_df, piezo_id, piezo_data, construct_data, annotate_df = None):
    fig2 = make_subplots(rows=2, cols=1, row_heights=[60,30], specs=[[{"secondary_y": True}],
                                                                   [{"secondary_y": False}]], shared_xaxes=True,
                                                                   vertical_spacing = 0.05)
    
    mini_maxi_dh = (math.inf,-math.inf,pd.Timestamp.max,pd.Timestamp.min)
    fig2.add_trace(go.Scatter(x=constructed_df.index,  y=constructed_df[construct_data],name=constructed_df.iloc[0,0]),row=1, col=1, secondary_y=True)
    st.table(fig2)
    piezo_list = list(set(piezo_df[piezo_id].tolist()))
    
    for id_dh in piezo_list:
        df_1 = piezo_df.loc[piezo_df[piezo_id]==id_dh]
        df_daily_1 = df_1.resample('D').max()
        df_daily_1 = df_daily_1.interpolate('linear')
        df_daily_1['dh'] = df_daily_1[piezo_data].diff()/df_daily_1.index.to_series().diff().dt.days
        df_daily_1 = df_daily_1.dropna()
        
        fig2.add_trace(go.Scatter(x=df_1.index, y=df_1[piezo_data],name=id_dh),row=1, col=1)
        fig2.add_trace(go.Scatter(x=df_1.index, y=df_daily_1['dh'],name=f"{id_dh}-dh"),row=2, col=1)
        mini_maxi_dh_loop = mini_maxi(df_daily_1,'dh')
        mini_maxi_dh = min_max_in_tuples(mini_maxi_dh, mini_maxi_dh_loop)
    
    mini_maxi_df = mini_maxi(piezo_df,piezo_data)
    mini_maxi_load = mini_maxi(constructed_df,construct_data)
    min_max_tuples = min_max_in_tuples(mini_maxi_df, mini_maxi_load)
    
    y_range = mini_maxi_df[1]-mini_maxi_df[0]
    y_add = (10*y_range)/100
    
    x_range = (min_max_tuples[3]-min_max_tuples[2]).days
    x_add = (2*x_range)/100
    x_add = timedelta(days=x_add)
    if annotate_df is not None:
        try:
            for index, row in annotate_df.iterrows():
                xs=row[0]
                xe=row[0]
                fig2.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_df[0],mini_maxi_df[1]],name=row[1],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=1, col=1)
                fig2.add_annotation(text=row[1], x=xs-x_add, y=mini_maxi_df[0]+y_add, showarrow=False,textangle=-90,opacity=0.5, font=dict(color="grey"))
                fig2.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_dh[0],mini_maxi_dh[1]],name=row[1],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=2, col=1)
        except Exception:
            st.table(annotate_df)
            pass
    
    fig2.update_layout(height=850, xaxis2_title = 'Time',yaxis1_title='Porewater pressure (kPa)', yaxis2_title="Construction height (m)", yaxis3_title="kPa/day")
    st.plotly_chart(fig2,use_container_width=True)
    
def c_and_t_plot(constructed_df, crest_df, toe_df, crest_id, toe_id, construct_data, crest_data, toe_data, annotate_df = None):
    fig3 = make_subplots(rows=2, cols=1, row_heights=[60,30], specs=[[{"secondary_y": True}],
                                                                       [{"secondary_y": False}]], shared_xaxes=True,
                                                                       vertical_spacing = 0.05)
        
    mini_maxi_dh = (math.inf,-math.inf,pd.Timestamp.max,pd.Timestamp.min)
        
    crest_df[crest_data] = crest_df[crest_data].abs()
    
    fig3.add_trace(go.Scatter(x=constructed_df.index,
                             y=constructed_df[construct_data],
                             name=constructed_df.iloc[0,0]),row=1, col=1, secondary_y=True)
    
    crest_list = list(set(crest_df[crest_id].tolist()))
        
    for id_dh in crest_list:
        df_2 = crest_df.loc[crest_df[crest_id]==id_dh]
        df_daily_2 = df_2.resample('D').max()
        df_daily_2 = df_daily_2.interpolate('linear')
        df_daily_2['dh'] = df_daily_2[crest_data].diff()/df_daily_2.index.to_series().diff().dt.days
        df_daily_2 = df_daily_2.dropna()
        
        fig3.add_trace(go.Scatter(x=df_2.index, y=df_2[crest_data],name=id_dh,mode='lines'),row=1, col=1)
        fig3.add_trace(go.Scatter(x=df_daily_2.index, y=df_daily_2['dh'],name=f"{id_dh}-dh",mode='lines'),row=2, col=1)
        mini_maxi_dh_loop = mini_maxi(df_daily_2,'dh')
        mini_maxi_dh = min_max_in_tuples(mini_maxi_dh, mini_maxi_dh_loop)
        
        
    toe_df[toe_data] = toe_df[toe_data].abs()
        
    toe_list = list(set(toe_df[toe_id].tolist()))
    
    for id_dh in toe_list:
        df_3 = toe_df.loc[toe_df[toe_id]==id_dh]
        df_daily_3 = df_3.resample('D').max()
        df_daily_3 = df_daily_3.interpolate('linear')
        df_daily_3['dh'] = df_daily_3[toe_data].diff()/df_daily_3.index.to_series().diff().dt.days
        df_daily_3 = df_daily_3.dropna()
        
        fig3.add_trace(go.Scatter(x=df_3.index, y=df_3[toe_data],name=id_dh,mode='lines'),row=1, col=1)
        fig3.add_trace(go.Scatter(x=df_daily_3.index, y=df_daily_3['dh'],name=f"{id_dh}-dh",mode='lines'),row=2, col=1)
        mini_maxi_dh_loop = mini_maxi(df_daily_3,'dh')
        mini_maxi_dh=min_max_in_tuples(mini_maxi_dh, mini_maxi_dh_loop)

            
    mini_maxi_df_toe = mini_maxi(toe_df,toe_data)
    mini_maxi_crest = mini_maxi(crest_df,crest_data)
        
    mini_maxi_df = min_max_in_tuples(mini_maxi_crest, mini_maxi_df_toe)
        
    mini_maxi_load = mini_maxi(constructed_df,construct_data)
    min_max_tuples = min_max_in_tuples(mini_maxi_df, mini_maxi_load)
        
    y_range = mini_maxi_df[1]-mini_maxi_df[0]
    y_add = (10*y_range)/100
        
    x_range = (min_max_tuples[3]-min_max_tuples[2]).days
    x_add = (2*x_range)/100
    x_add = timedelta(days=x_add)
    
    if annotate_df is not None:
        try:
            for index, row in annotate_df.iterrows():
                xs=row[0]
                xe=row[0]
                fig3.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_df[0],mini_maxi_df[1]],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=1, col=1)
                fig3.add_annotation(text=row[1], x=xs-x_add, y=mini_maxi_df[0]+y_add, showarrow=False,textangle=-90,opacity=0.5, font=dict(color="grey"))
                fig3.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_dh[0],mini_maxi_dh[1]],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=2, col=1)
        except Exception:
            pass
            
    fig3.update_layout(height=800, xaxis2_title = 'Time',yaxis1_title='Crest and Toe Movement (m)', yaxis1_autorange="reversed", yaxis2_title="Construction height (m)", yaxis3_title="mm/day")
    st.plotly_chart(fig3,use_container_width=True)  
    
def pwp_and_fos(constructed_df, piezo_df, piezo_id, construct_id, construct_data, piezo_data, vwp_list, unit_water, level_water,
                unit_soil, unit_fill, ratio_s, annotate_df = None):
    fig4 = make_subplots(rows=2, cols=1, row_heights=[60,30], specs=[[{"secondary_y": True}],
                                                                        [{"secondary_y": False}]], shared_xaxes=True,
                                                                        vertical_spacing = 0.05)
        
    mini_maxi_dh = (math.inf,-math.inf,pd.Timestamp.max,pd.Timestamp.min)
    piezo_list = list(set(piezo_df[piezo_id].tolist()))
    
    for key, val in vwp_list.items():
        for id_du in piezo_list:
            if id_du == key:
                df = piezo_df.loc[piezo_df[piezo_id]==id_du]
                df[piezo_data] = df[piezo_data].abs()
                df = df.resample('D').agg({piezo_id: 'first',piezo_data: 'mean'}) #was previously resample('D').mean()
                df = df.interpolate('linear')
                constructed_df = constructed_df.resample('D').agg({construct_id: 'first',construct_data: 'mean'})
                constructed_df = constructed_df.interpolate('linear')
                df = pd.merge(df,constructed_df,left_index=True, right_index=True)
                
                df['pp'] = (df[piezo_data]*unit_water)
                df['epp'] = df['pp']-((abs(val-level_water))/(1/unit_water))
                fig4.add_trace(go.Scatter(x=df.index, y=df['epp'], name=id_du))
                mini_maxi_dh_loop = mini_maxi(df,'epp')
                mini_maxi_dh = min_max_in_tuples(mini_maxi_dh, mini_maxi_dh_loop)
                    
                df['sv'] = (unit_soil*val)+(unit_fill*df[construct_data])
                df['svp'] = df['sv']-df['pp']
                df['su'] = ratio_s*df['svp']
                df['fos'] = (5.14*df['su'])/(unit_fill*df[construct_data])
                fig4.add_trace(go.Scatter(x=df.index, y=df['fos'],name=f"{id_du}-FoS"),row=2, col=1)
              
                    
    fig4.add_trace(go.Scatter(x=constructed_df.index, y=constructed_df[construct_data],name=constructed_df.iloc[0,0]),secondary_y=True,)
    mini_maxi_load = mini_maxi(constructed_df,construct_data)
    min_max_tuples = min_max_in_tuples(mini_maxi_dh, mini_maxi_load)
        
    y_range = mini_maxi_dh[1]-mini_maxi_dh[0]
    y_add = (10*y_range)/100
        
    x_range = (min_max_tuples[3]-min_max_tuples[2]).days
    x_add = (2*x_range)/100
    x_add = timedelta(days=x_add)
    
    if annotate_df is not None:
        try:
            for index, row in annotate_df.iterrows():
                xs=row[0]
                xe=row[0]
                fig4.add_trace(go.Scatter(x=[xs,xe], y=[mini_maxi_dh[0],mini_maxi_dh[1]],name=row[1],opacity=0.5,showlegend=False, line=dict(color='grey', dash='dash')),row=1, col=1)
                fig4.add_annotation(text=row[1], x=xs-x_add, y=mini_maxi_dh[0]+y_add, showarrow=False,textangle=-90,opacity=0.5, font=dict(color="grey"))
        except Exception:
            pass
        
    fig4.update_layout(height=800, xaxis2_title = 'Time',yaxis1_title='Excess Pore Pressure (kPa)',yaxis2_title="Construction height (m)", yaxis3_title="FoS")
    st.plotly_chart(fig4,use_container_width=True)
    
def pair_s_and_t_plot(settled_df, toe_df, settle_id, toe_id, settle_data, toe_data, st_pair):
    x = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,1.1,1.2,1.3,1.4]
    s1 = [4.27,3.16,2.39,1.86,1.48,1.22,1.02,0.88,0.78,0.70,0.66,0.63,0.61,0.62]
    s09 = [2.19,1.73,1.38,1.10,0.89,0.73,0.60,0.49,0.41,0.35,0.29,0.25]
    s08 = [1.63,0.99,0.65,0.47,0.38,0.33,0.31,0.32]
    s07 = [1.08,0.53,0.32,0.23,0.20,0.22]
    s06 = [0.50,0.28,0.18,0.13,0.11,0.10]

    settled_df[settle_data] = settled_df[settle_data].abs()
    toe_df[toe_data] = toe_df[toe_data].abs()
    table_df = pd.DataFrame([])
    name_list = []

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=x, y=s1,mode="lines",name="S(1)",line_shape='spline',showlegend=False, line=dict(color='grey')))
    fig5.add_trace(go.Scatter(x=x, y=s09,mode="lines",name="S(0.9)",line_shape='spline',showlegend=False, line=dict(color='grey')))
    fig5.add_trace(go.Scatter(x=x, y=s08,mode="lines",name="S(0.8)",line_shape='spline',showlegend=False, line=dict(color='grey')))
    fig5.add_trace(go.Scatter(x=x, y=s07,mode="lines",name="S(0.7)",line_shape='spline',showlegend=False, line=dict(color='grey')))
    fig5.add_trace(go.Scatter(x=x, y=s06,mode="lines",name="S(0.6)",line_shape='spline',showlegend=False, line=dict(color='grey')))
    
    for settle_settle,toe_toe in st_pair.items() :
        df1 = settled_df[(settled_df[settle_id]==settle_settle)]
        df1 = df1.rename(columns={settle_data: "mov c"})
        df1 = df1.rename(columns={settle_id: "id1"})
        idcol = df1["id1"]
        df1 = df1.resample('D').max()
        df1 = df1.interpolate('linear')
        df1["id1"] = idcol
        
        df2 = toe_df[(toe_df[toe_id]==toe_toe)]
        df2 = df2.rename(columns={toe_data: "mov t"})
        df2 = df2.rename(columns={toe_id: "id2"})
        idcol = df2["id2"]
        df2 = df2.resample('D').max()
        df2 = df2.interpolate('linear')
        df2["id2"] = idcol
        
                    
        df_concat = pd.merge(df1,df2,left_index=True, right_index=True)
        df_concat = df_concat.dropna()
        df_concat['ct_over_s'] = df_concat["mov t"]/df_concat["mov c"]
        df_concat['settlement_meters'] = df_concat["mov c"]/1000
        fig5.add_trace(go.Scatter(x=df_concat['ct_over_s'], y=df_concat['settlement_meters'],mode='markers',name=df_concat.iloc[0]["id1"]+"-"+df_concat.iloc[0]["id2"]))
              
        first_ct_over_s = df_concat['ct_over_s'].iloc[0]
        first_s = df_concat['mov c'] .iloc[0]           
        last_ct_over_s = df_concat['ct_over_s'].iloc[-1] # was previously df_concat.iloc[-1]['ct_over_s']
        last_s = df_concat.iloc[-1]['mov c']
        date_s = df_concat.index.values[0]
        date_e = df_concat.index.values[-1]
        date_diff = (date_e - date_s)
        days = int(date_diff) 

        X = df_concat[:]['ct_over_s'].values.reshape(-1, 1)  # values converts it into a numpy array
        X_train, X_test, y_train, y_test = train_test_split(X, df_concat['mov c'], random_state=0)

        linear_regressor = LinearRegression() 
        linear_regressor.fit(X_train, y_train)

        slope= linear_regressor.coef_[0]
        intercept= linear_regressor.intercept_
        x_reg=[0,0.5,1,1.5]
        y_reg=[]
        for xu in x_reg:
            yu = (slope*xu) + intercept
            y_reg.append(yu)

        line_1 = LineString(np.column_stack((pd.Series(x_reg),pd.Series(y_reg))))
        line_2 = LineString(np.column_stack((pd.Series(x),pd.Series(s1))))
        intersection = line_1.intersection(line_2).wkt
        intersection = intersection.replace("POINT ", "")
        intersection = intersection.replace("(", "")
        intersection = intersection.replace(")", "")
        intersection = intersection.split(" ")
        fig5.add_trace(go.Scatter(x=pd.DataFrame([round(float(intersection[0]),2)]),y=pd.DataFrame([round(float(intersection[1]),2)]),mode='markers',
                                  name='Intersection for ' + df_concat.iloc[0]["id1"] + "-" + df_concat.iloc[0]["id2"], marker = dict(color='rgb(127, 127, 127)')))
        intersection = [float(i) for i in intersection]

        dist1 = distance.euclidean([first_ct_over_s,first_s], [last_ct_over_s,last_s])
        dist2 = distance.euclidean(intersection, [last_ct_over_s,last_s])

        days_to_fos = (dist2*days)/dist1
        name_list.append(df_concat.iloc[0]["id1"]+"-"+df_concat.iloc[0]["id2"])
        table_df = pd.concat([table_df,pd.DataFrame([int(days_to_fos)])])
            
        
    table_df.columns = ['Estimated days to FoS = 1']
    table_df.index = name_list
    
    fig5.add_annotation(text="q/qf=1.0", x=1.3, y=0.75, showarrow=False, font=dict(color="grey"))
    fig5.update_layout(height=600)
    fig5.update_xaxes(title_text="Ratio Toe Displacement / Settlement")
    fig5.update_yaxes(title_text="Settlement (m)")
    
    st.plotly_chart(fig5, use_container_width=True)
    st.table(table_df)
    
def asaoka_plot(settled_df, settle_id, settle_data):
    fig6 = go.Figure()
    table_stats = pd.DataFrame()    
    settle_list = list(set(settled_df[settle_id].tolist()))
    
    for i in range(len(settle_list)):
        id_asaoka = settle_list[i]
        df = settled_df[(settled_df[settle_id]==id_asaoka)]
        df = df.resample('D').max()
        df = df.interpolate('linear')
        df[settle_data] = abs(df[settle_data])
        df['pk+1'] = df[settle_data].shift(-1)
        df = df.dropna()
        df_current = df.iloc[-1][settle_data]
        fig6.add_trace(go.Scatter(x=df['pk+1'], y=df[settle_data],name=id_asaoka,mode='markers',marker = dict(color=colors[(i*2)%8])))
            
        #Linear Regression
        X = df[:]['pk+1'].values.reshape(-1, 1)  # values converts it into a numpy array
        X_train, X_test, y_train, y_test = train_test_split(X, df[settle_data], random_state=0)
            
        linear_regressor = LinearRegression() 
        linear_regressor.fit(X_train, y_train)
        x_range = np.linspace(X.min(), X.max())
        y_range = linear_regressor.predict(x_range.reshape(-1, 1))
            
        slope = linear_regressor.coef_[0]
        intercept = linear_regressor.intercept_
        table_stats = pd.concat([table_stats,pd.DataFrame([id_asaoka,slope,round(intercept,2),round(intercept/(1-slope),2),round((intercept/(1-slope))-abs(df_current),2)])])
        
        fig6.add_trace(go.Scatter(x=x_range, y=y_range,name=id_asaoka+"- Predicted line", line = dict(color=colors[(i*2 + 1)%8])))
        
    table_stats = table_stats.rename(columns={0:'Instrument',1:'Gradient',2:'Intercept', 3:'Ultimate settlement', 4:'Difference to current'})
    table_stats = table_stats.reset_index(drop=True)  
                
    fig6.update_layout(height=600)
    fig6.update_xaxes(title_text="S")
    fig6.update_yaxes(title_text="Sn+1")
    
    st.plotly_chart(fig6, use_container_width=True)
    st.table(table_stats)
    
def guo_chu_plot(settled_df, settle_id, settle_data):
    fig7 = go.Figure()
    table_stats_2 = pd.DataFrame()
    settle_list = list(set(settled_df[settle_id].tolist()))
    
    for i in range(len(settle_list)):
        id_guo = settle_list[i]
        df = settled_df[(settled_df[settle_id]==id_guo)]
        df = df.resample('D').max()
        df = df.interpolate('linear')
        df['pk'] = abs(df[settle_data])**(5/3)
        df['pk+1'] = abs(df[settle_data].shift(-1))**(5/3)
        df = df.dropna()
        df_current = df.iloc[-1][settle_data]
        fig7.add_trace(go.Scatter(x=df['pk+1'], y=df['pk'],name=id_guo,mode='markers',marker = dict(color=colors[(i*2)%8])))
        
        #Linear Regression
        X = df[:]['pk+1'].values.reshape(-1, 1)  # values converts it into a numpy array
        X_train, X_test, y_train, y_test = train_test_split(X, df['pk'], random_state=0)
        
        linear_regressor = LinearRegression() 
        linear_regressor.fit(X_train, y_train)
        x_range = np.linspace(X.min(), X.max())
        y_range = linear_regressor.predict(x_range.reshape(-1, 1))
        
        slope = linear_regressor.coef_[0]
        intercept = linear_regressor.intercept_
        table_stats_2 = pd.concat([table_stats_2,pd.DataFrame([id_guo,slope,round(intercept,2),round((intercept/(1-slope))**0.6,2),round((intercept/(1-slope))**0.6-abs(df_current),2)])])
    
        fig7.add_trace(go.Scatter(x=x_range, y=y_range,name=id_guo+"- Predicted line", line = dict(color=colors[(i*2 + 1)%8])))
    
    #Difference to current Passing Criteria on Target
    table_stats_2 = table_stats_2.rename(columns={0:'Instrument',1:'Gradient',2:'Intercept', 3:'Ultimate settlement', 4:'Difference to current'})
    table_stats_2 = table_stats_2.reset_index(drop=True)   
                          
    fig7.update_layout(height=600)
    fig7.update_xaxes(title_text="S")
    fig7.update_yaxes(title_text="Sn+1")
    
    st.plotly_chart(fig7, use_container_width=True)
    st.table(table_stats_2)

#Start of page
st.markdown("This data interpretation tool was prepared as part of the Digital Committee PMO’s Optimisation Programme by Fabien Blanchais and Kalyan Kamepalli. The tool is a practice approved tool of the Geotechnics Practice.")

st.markdown('''
            The tool produces the following plots:
            - Settlement vs. Time in relation to the height of the embankment
            - Piezo level vs. Time in relation to the height of the embankment
            - Crest and toe movement vs. Time in relation to the height of the embankment
            - Excess Pore Pressure vs. Time in relation to the height of the embankment
            - Factor of Safety vs. Time in relation to the height of the embankment
            - Embankment stability control chart based on Watika and Matsuo (1994)
            - Ultimate settlement based on Asaoka (1978)
            - Ultimate settlement based on Guo and Chu (1977)
            ''')

st.markdown('''
            The following references were used:
            - Duncan, N. et al. (1999). The Observational Method in Ground Engineering: Principles and Applications, CIRIA Report 185
            - Asaoka, A. (1978). Observational Procedure of Settlement Prediction. Soils and Foundations, 18(4), pp 87-101
            - Matuso, M & Kawamura, K.(1977). Diagram for construction control of embankment on soft ground. Soild and Foundations, 17(3), pp 37-52
            ''')
            


st.markdown("**Import files**")
col25,col26 = st.columns([2,2])
col27,col28 = st.columns([2,2])
col29,col30 = st.columns([2,2])
annotate = col25.file_uploader("Annotation",type=('csv','xlsx'),accept_multiple_files=True)
settled = col26.file_uploader("Settlement",type=('csv','xlsx'),accept_multiple_files=True)
constructed = col27.file_uploader("Construction",type=('csv','xlsx'),accept_multiple_files=True)
piezoed = col28.file_uploader("Piezo",type=('csv','xlsx'),accept_multiple_files=True)
crested = col29.file_uploader("Crest",type=('csv','xlsx'),accept_multiple_files=True)
toed = col30.file_uploader("Toe",type=('csv','xlsx'),accept_multiple_files=True) 
done = st.button('Done', key='done uploading')

if done: 
    st.session_state.key = 'uploader done'
    st.session_state['uploader done'] = 'done upload'

if 'uploader done' in st.session_state:   
        try:
            annotate_df,annotate_col = files_to_df(annotate)
        except:
            annotate_df = pd.DataFrame() # must create empty dataframe to avoid error
            annotate_col = [None]
        try:
            settled_df,settled_col = files_to_df(settled)
        except:
            settled_col = [None]
        try:    
            constructed_df,constructed_col = files_to_df(constructed)
        except:
            constructed_col = [None]
        try:
            piezo_df,piezo_col = files_to_df(piezoed)
        except:
            piezo_col = [None]
        try:
            crest_df,crest_col = files_to_df(crested)
        except:
            crest_col = [None]
        try:
            toe_df,toe_col = files_to_df(toed)
        except:
            toe_col = [None]
        
        
        st.markdown('**Select column headers in dropdowns**')
        col1,col2,col3,col4,col5,col6 = st.columns([1,1,1,1,1,1])
        col7,col8,col9,col10,col11,col12 = st.columns([1,1,1,1,1,1])
        col13,col14,col15,col16,col17,col18 = st.columns([1,1,1,1,1,1])
        
        col1.markdown('ID')
        settle_id = col2.selectbox(' ',options=settled_col,key='settle id')
        construct_id = col3.selectbox(' ',options=constructed_col,key='construct id')
        piezo_id = col4.selectbox(' ',options=piezo_col,key='piezo id')
        crest_id = col5.selectbox(' ',options=crest_col,key='crest id')
        toe_id = col6.selectbox(' ',options=toe_col,key='toe id')
        
        col7.markdown('Datetime')
        settle_date = col8.selectbox(' ',options=settled_col,key='settle date')
        construct_date = col9.selectbox(' ',options=constructed_col,key='construct date')
        piezo_date = col10.selectbox(' ',options=piezo_col,key='piezo date')
        crest_date = col11.selectbox(' ',options=crest_col,key='crest date')
        toe_date = col12.selectbox(' ',options=toe_col,key='toe date')
        
        col13.markdown('Data')
        settle_data = col14.selectbox(' ',options=settled_col,key='settle data')
        construct_data = col15.selectbox(' ',options=constructed_col,key='construct data')
        piezo_data = col16.selectbox(' ',options=piezo_col,key='piezo data')
        crest_data = col17.selectbox(' ',options=crest_col,key='crest data')
        toe_data = col18.selectbox(' ',options=toe_col,key='toe data')
        
        done_button = st.button('Show plots',key='ok')
        
        try:
            annotate_df.iloc[:,0]= pd.to_datetime(annotate_df.iloc[:,0],dayfirst=True)
            st.session_state.key = ['annotate df']
            st.session_state['annotate df'] = annotate_df
        except Exception:
                pass
        
        try:
            settled_df[settle_date]= pd.to_datetime(settled_df[settle_date],dayfirst=True)
            settled_df = settled_df.set_index(settle_date).sort_index()
            st.session_state.key = ['settled df']
            st.session_state['settled df'] = settled_df
        except Exception:
                pass
    
        try:
            constructed_df[construct_date]= pd.to_datetime(constructed_df[construct_date],dayfirst=True)
            constructed_df = constructed_df.set_index(construct_date).sort_index()
            st.session_state.key = ['constructed df']
            st.session_state['constructed df'] = constructed_df
        except Exception:
                pass   
        
        try:
            piezo_df[piezo_date]= pd.to_datetime(piezo_df[piezo_date],dayfirst=True)
            piezo_df = piezo_df.set_index(piezo_date).sort_index()
            st.session_state.key = ['piezo df']
            st.session_state['piezo df'] = piezo_df
        except Exception:
                pass
        
        try:
            crest_df[crest_date]= pd.to_datetime(crest_df[crest_date],dayfirst=True)
            crest_df = crest_df.set_index(crest_date).sort_index()
            st.session_state.key = ['crest df']
            st.session_state['crest df'] = crest_df
        except Exception:
                pass
            
        try:
            toe_df[toe_date]= pd.to_datetime(toe_df[toe_date],dayfirst=True)
            toe_df = toe_df.set_index(toe_date).sort_index()
            st.session_state.key = ['toe df']
            st.session_state['toe df'] = toe_df
        except Exception:
                pass
        
        if done_button:
            st.session_state.key=['graph time']
            st.session_state['graph time']='ok'
        
if 'graph time' in st.session_state:
    if 'annotate df' in st.session_state:
        annotate_df = st.session_state['annotate df']
    else:
        annotate_df = None
        
    if 'settled df' in st.session_state:
        settled_df = st.session_state['settled df']
        
    if 'constructed df' in st.session_state: 
        constructed_df = st.session_state['constructed df']
    
    if 'piezo df' in st.session_state:
        piezo_df = st.session_state['piezo df']
        
    if 'crest df' in st.session_state:  
        crest_df = st.session_state['crest df']
        
    if 'toe df' in st.session_state:    
        toe_df = st.session_state['toe df'] 
    
    settle_id = st.session_state['settle id']
    constructed_id = st.session_state['construct id']
    piezo_id = st.session_state['piezo id']
    crest_id = st.session_state['crest id']
    toe_id = st.session_state['toe id'] 
    
    settle_date = st.session_state['settle date']
    construct_date = st.session_state['construct date']
    piezo_date = st.session_state['piezo date']
    crest_date = st.session_state['crest date']
    toe_date = st.session_state['toe date']
    
    settle_data = st.session_state['settle data']
    construct_data = st.session_state['construct data']
    piezo_data = st.session_state['piezo data']
    crest_data = st.session_state['crest data']
    toe_data = st.session_state['toe data']
    
    st.markdown("""---""")
    
    settle_button = st.button('Settlement plots', key='click1')
    
    if annotate_col == [None]:
        try:
            settlement_plot(settled_df,constructed_df,settle_id,settle_data,construct_data)
        except:
            st.error('Cannot create graph due to missing data!')
    else:
        try:
            settlement_plot(settled_df,constructed_df,settle_id,settle_data,construct_data,annotate_df)
        except Exception as e:
            st.write(e)
            st.error('Cannot create graph due to missing data!')
        
    st.session_state.key = 'settle button'
    st.session_state['settle button']='done'
        
    st.markdown("""---""")
    
    piezo_button = st.button('Piezo plots')
    
    if annotate_col == [None]:
        try:
            piezo_plot(piezo_df,constructed_df,piezo_id,piezo_data,construct_data)  
        except:
            st.error('Cannot create graph due to missing data!')
    else:
        try:
            piezo_plot(piezo_df,constructed_df,piezo_id,piezo_data,construct_data,annotate_df)  
        except:
            st.error('Cannot create graph due to missing data!')
        
    st.markdown("""---""")
    
    c_and_t_button= st.button('Crest and Toe plots')
    
    if annotate_col == [None]:
        try:
            c_and_t_plot(constructed_df, crest_df, toe_df, crest_id, toe_id, construct_data, crest_data, toe_data)
        except:
            st.error('Cannot create graph due to missing data!')
    else:
        try:
            c_and_t_plot(constructed_df, crest_df, toe_df, crest_id, toe_id, construct_data, crest_data, toe_data, annotate_df)
        except:
            st.error('Cannot create graph due to missing data!')
        
    st.markdown("""---""")
    
    col19,col20 = st.columns([1,1])
    unit_water = col19.number_input('Unit weight of water', value=9.81, step=0.01, disabled=False, key='unit weight water')
    level_water = col20.number_input('Water level (mbgl)', value=0.00, step=0.01, disabled=False, key='water level')
            
    col21,col22 = st.columns([1,1])
    unit_soil = col21.number_input('Unit weight of soil', value=0.00, step=0.01, disabled=False, key='unit weight soil')
    unit_fill = col22.number_input('Unit weight of fill', value=0.00, step=0.01, disabled=False, key='unit weight fill')
    
    col23,col24 = st.columns([1,1])
    ratio_s = col23.number_input('Ratio of s$_u$ to s', value=0.00, step=0.01, disabled=False, key='ratio of su')
    
    vwp_dict = {}
    try:
        for name in list(set(piezo_df[piezo_id].tolist())):
            col25,col26 = st.columns([1,1])
            vwp_depth = col25.number_input(f'{name} depth (mbgl)', value=0.00, step=0.01, disabled=False, key=f'{name} Depth')
            vwp_dict[name] = vwp_depth
    except:
         pass
    pwp_button = st.button('Excess PWP & FoS Plot')
    
    if annotate_col == [None]:
        try:
            pwp_and_fos(constructed_df, piezo_df, piezo_id, construct_id, construct_data, piezo_data, vwp_dict, unit_water, level_water, unit_soil, unit_fill, ratio_s)  
        except:
            st.error('Cannot create graph due to missing data!')
    else:
        try:
            pwp_and_fos(constructed_df, piezo_df, piezo_id, construct_id, construct_data, piezo_data, vwp_dict, unit_water, level_water, unit_soil, unit_fill, ratio_s, annotate_df)  
        except:
            st.error('Cannot create graph due to missing data!')
        
    st.markdown("""---""")
    
    st.markdown('**Pair Settlement and Toe instruments**')
    try:
        length = max(len(settled_df[settle_id].unique()),len(toe_df[toe_id].unique()))
        st_pair=dict()
        for i in range(length):
            col23,col24 = st.columns([1,1])
            settlement_box = col23.selectbox('Settlement', options = settled_df[settle_id].unique(),key=f'settlement box{i}')
            toe_box = col24.selectbox('Toe', options = toe_df[toe_id].unique(), key=f'toe{i}')
            st_pair[settlement_box] = toe_box
    except:
        pass
    stable_button = st.button('Stability Plot')
    
    try:
        pair_s_and_t_plot(settled_df, toe_df, settle_id, toe_id, settle_data, toe_data, st_pair)
    except:
        st.error('Cannot create graph due to missing data!')
        
    st.markdown("""---""")
    
    asaoka_button = st.button('Asaoka')
    
    #try:
    asaoka_plot(settled_df, settle_id, settle_data)
    #except:
        #st.error('Cannot create graph due to missing data!')
    
    st.markdown("""---""")
    
    guo_chu_button = st.button('Guo & Chu')
    
    #try:
    guo_chu_plot(settled_df, settle_id, settle_data)
    #except:
        #st.error('Cannot create graph due to missing data!')
    
    
     
