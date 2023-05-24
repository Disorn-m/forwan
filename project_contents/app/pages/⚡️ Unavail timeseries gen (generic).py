#!/usr/bin/env python
# coding: utf-8

# In[27]:

import streamlit as st
import pandas as pd 
import numpy as np
import datetime
import io


# In[28]:


#AV_DATA['Start day_Start hour'][1].floor(freq = 'H')  // To truncate to hour
from bisect import bisect_left, bisect_right

def Binary_left_Search(a, x):
    i = bisect_left(a, x)
    if x == a[i]:
        return i
    elif x < a[i] :
        return i-1
    else:
        return -1

def Binary_right_Search(a, x):
    i = bisect_right(a, x)
    if x == a[i-1]:
        return i-1
    elif x < a[i] :
        return i
    else:
        return -1

def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

# In[31]:


# import the library
#from google_trans_new import google_translator

#https://towardsdatascience.com/translate-a-pandas-data-frame-using-googletrans-library-fb0aa7fca592


# In[29]:


#translator = google_translator()
#translate_text = translator.translate('สวัสดีจีน',lang_tgt='en') 
#print(translate_text)


# In[29]:


# Driver code
#a  = [1, 2, 4, 4, 8]
#x = int(4)
#res = Binary_right_Search(a, x)
#if res == -1:
#    print("No value smaller than ", x)
#else:
#    print("Largest value smaller than ", x, " is at index ", res)


# In[1]:

#Create tab to input date format of data (WIP currently interface only)
st.markdown("\n")
st.markdown('Please select the **Start date and time**')
col1, col2 = st.columns(2)
with col1:
    #Create date format selector
    date_format = st.selectbox('Date format', ('%d/%m/%Y %H:%M', '%m/%d/%Y %H:%M', '%Y/%m/%d %H:%M'))
with col2:
    st.write('Selected format:', date_format)


#Create the tab to input the start date and time
st.markdown("\n")
st.markdown('Please select the **Start date and time**')
col1, col2, col3, col4 = st.columns(4)
with col1:
    # Create a date selector widget
    s_date = st.date_input("Choose a **start DATE**:")

with col2:
    s_hour = st.selectbox("Select **start HOUR**:", list(range(24)))
    #st.write("You selected:", s_hour)

with col3:
    s_minute = st.selectbox("Select **start MINUTE**:", list(range(60)))
    #st.write("You selected:", s_minute)

with col4:
    # Create a time value from the hour and minute
    s_time = datetime.time(hour=s_hour, minute=s_minute)
    # Combine the selected date and time
    s_date_time = f"{s_date} {s_time}"
    
    # Display the selected date and time on the main page
    st.write("**Selected start date and time:**", s_date_time)


#Create the tab to input the end date and time
st.markdown('Please select the **End date and time**')
col1, col2, col3, col4 = st.columns(4)
with col1:
    # Create a date selector widget
    e_date = st.date_input("Choose a **end DATE**:")

with col2:
    e_hour = st.selectbox("Select **end HOUR**:", list(range(24)))
    #st.write("You selected:", e_hour)

with col3:
    e_minute = st.selectbox("Select **end MINUTE**:", list(range(60)))
    #st.write("You selected:", e_minute)

with col4:
    # Create a time value from the hour and minute
    e_time = datetime.time(hour=e_hour, minute=e_minute)
    # Combine the selected date and time
    e_date_time = f"{e_date} {e_time}"
    
    # Display the selected date and time on the main page
    st.write("**Selected end date and time:**", e_date_time)


# Allow the user to input total number of inverters in the Project
st.markdown('**Information based on uploaded file**')
col1, col2 = st.columns(2)
with col1:
    total_inv = st.number_input('Total number of inverters in the project', min_value=1, value=1, step=1)
with col2:
    st.write("Total number of inverters:**", total_inv)

# Allow the user to upload an CSV file
uploaded_file = st.file_uploader("**Choose a CSV file:**")

if uploaded_file is not None:
    st.markdown('**Information based on uploaded file**')
    # Read the CSV file into a pandas DataFrame
    df_av1 = pd.read_csv(uploaded_file)

    # Name the columns
    df_av1.columns = ['No.','Start time','End time','PCS','Downed units','Details']

    # Check number of timestep data
    # Find the minimum and maximum values in the first two columns
    min_value_1 = df_av1['No.'].min()
    max_value_1 = df_av1['No.'].max()

    number_input_timestep_data = max_value_1 - min_value_1 +1
    st.write(f"Number of input timestep: {number_input_timestep_data}")
    df_av1
    df_av1['Start time'] = pd.to_datetime(df_av1['Start time'], format= '%d/%m/%Y %H:%M')
    df_av1['End time'] = pd.to_datetime(df_av1['End time'], format= '%d/%m/%Y %H:%M')
    # Check the min max of datetime
    min_value_2 = df_av1['Start time'].min()
    st.write(f"Start: {min_value_2}")
    max_value_3 = df_av1['End time'].max()
    st.write(f"End: {max_value_3}")
    
    #used to print dataframe in streamlit
    buffer = io.StringIO()
    df_av1.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)


# In[31]:


## Making sure datetime is parsed.
df_av1['Start time'] = pd.to_datetime(df_av1['Start time'])
df_av1['End time'] = pd.to_datetime(df_av1['End time'])


# In[32]:


df_av1.columns

# In[33]:


df_av1_data = pd.DataFrame(columns = ['Start time','End time','kw_down','Downed units','PCS','JCB','StringST','reason'])

df_av1_data['Start time'] = df_av1['Start time'].copy()
df_av1_data['End time'] = df_av1['End time'].copy()
#df_av1_data['kw_down'] = df_av1['容量（Kw）'].copy()
df_av1_data['PCS'] = df_av1['PCS'].copy()
#df_av1_data['JCB'] = df_av1['接続箱ＣＢ'].copy()
#df_av1_data['StringST'] = df_av1['ストリングＳＴ'].copy()
df_av1_data['Downed units'] = df_av1['Downed units'].copy()
df_av1_data['reason'] = df_av1['Details'].copy()


# In[34]:


df_av1_data.head()

# #For dataframe 1
# # use translate method to translate a string - by default, the destination language is english
# 
# translations = {}
# #for column in df_en.columns:
#     # unique elements of the column
#     #unique_elements = df_en[column].unique()
# unique_elements = df_av1_data['reason'].unique()
# for element in unique_elements:
#     # add translation to the dictionary
#     translations[element] = translator.translate(element)
#     
# print(translations)
# 
# df_av1_data['en_reason'] = df_av1_data['reason'].copy()
# df_av1_data['en_reason'].replace(translations, inplace= True)
# df_av1_data.head()

# In[35]:


#making sure start and end time is valid
df_av1_data["valid start end?"] = df_av1['End time'] > df_av1['Start time']


# In[36]:


#create datetime range
ts_start = pd.to_datetime(s_date_time) #"1/3/2020 1AM"
ts_end = pd.to_datetime(e_date_time) #"31/12/2022 11.55PM"
ts_datetime = pd.date_range(start = ts_start, end = ts_end, freq = '1H')
ts_datetime

# In[37]:


#Create dict of data & col name

data_time_dict = { "datetime" : ts_datetime}

df_ts_only = pd.DataFrame(data_time_dict )
df_ts_only

# In[38]:


### Test time binary search

#time_step_start = pd.to_datetime("2020-11-16 10:31:00")

time_step_start = df_av1_data['Start time'][0]
ts_search_index1 = Binary_left_Search(df_ts_only['datetime'],time_step_start)

#time_step_end = pd.to_datetime("2020-11-17 16:48:00")
time_step_end = df_av1_data['End time'][0]
ts_search_index2 = Binary_right_Search(df_ts_only['datetime'],time_step_end)



print("search for " + str(time_step_start))
print(df_ts_only.loc[[ts_search_index1]])

#diff_in_min =  (time_step_start - df_ts_only['datetime'][ts_search_index1])/np.timedelta64(1,'m')
#print("diff in min:" + str(diff_in_min))

#for i in range(ts_search_index1,ts_search_index2):
#    print(df_ts_only.loc[[i]])


# In[39]:


ts_search_index1


# In[41]:


timestep_const = 60

df_ts = df_ts_only.copy()

for i in range(len(df_av1_data.index)):
    
    if df_av1_data['valid start end?'][i] == True :
        #Name column for each equipment downtime
        dt_column = df_av1_data['PCS'][i] + ("" if pd.isna(df_av1_data['JCB'][i]) else ("." + str(df_av1_data['JCB'][i]))) + ("" if pd.isna(df_av1_data['StringST'][i]) else ("." + str(df_av1_data['StringST'][i])))
        dt_column_weight = dt_column + "_weight"
        if dt_column not in df_ts.columns:
            df_ts[dt_column] = np.nan
            df_ts[dt_column_weight] = np.nan

        #Search for start time in time series
        time_step_start = df_av1_data['Start time'][i]

        #if time_step_start < df_ts_only['datetime'].max():
        ts_search_index1 = Binary_left_Search(df_ts['datetime'],time_step_start)

        if ts_search_index1 > 0 :
            #assign first timestep period
            start_min_delta = (df_ts['datetime'][ts_search_index1] - time_step_start)/np.timedelta64(1,'m') + timestep_const
            df_ts.loc[ts_search_index1,dt_column] = start_min_delta


        #assign period in between start and end timestep
        time_step_end = df_av1_data['End time'][i]
        ts_search_index2 = Binary_right_Search(df_ts['datetime'],time_step_end) - 1


        if ts_search_index2 > 0 :

            if ts_search_index1 < len(df_ts.index):
                mid_period1 = ts_search_index1 + 1
            else:
                mid_period1 = ts_search_index1

            mid_period2 = ts_search_index2 - 1

            df_ts.loc[mid_period1 : mid_period2 ,dt_column] = timestep_const

            #assign last timestep period
            end_min_delta = (time_step_end - df_ts['datetime'][ts_search_index2])/np.timedelta64(1,'m')
            df_ts.loc[ts_search_index2,dt_column] = end_min_delta

            #assign weight to each downtime
            df_ts.loc[ts_search_index1 : ts_search_index2 , dt_column_weight] = df_av1_data['Downed units'][i]
        


# In[48]:


#Selecting only weight column
weight_cols = [col for col in df_ts.columns if 'weight' in col]

df_ts_weight = df_ts.loc[:,weight_cols]
df_ts_weight.set_index(df_ts['datetime'], inplace= True)
df_ts_weight.head()


# In[49]:


#Selecting only downtime column
df_ts_downtime = df_ts.drop(columns= weight_cols)
df_ts_downtime = df_ts_downtime.drop(columns= 'datetime')
df_ts_downtime.set_index(df_ts['datetime'], inplace= True)
df_ts_downtime.head()


# In[50]:

#display all relevant df
st.markdown('DISPLAY DATAFRAMES')
#df_av1_data
st.markdown('df_ts')
df_ts
st.markdown('df_ts_weight')
df_ts_weight
st.markdown('df_ts_downtime')
df_ts_downtime


#multiplication of weight and downtime dataframes
df_ts_total_DT = df_ts_downtime.mul(df_ts_weight.values)
st.markdown('df_ts_downtime*df_ts_weight')
df_ts_total_DT

#process to make equivalent downtime dataframe
df_ts_equiv_DT = df_ts_total_DT.div(total_inv)
df_ts_equiv_DT

#summation of equivalent downtime per unit equipment
df_ts_total_equiv_DT = df_ts_equiv_DT.sum(axis=0)
df_ts_total_equiv_DT


#Download button

csv = convert_df(df_ts_equiv_DT)

st.download_button(
    "Press to Download df_ts-equiv_DT",
    csv,
    "unavailability.csv",
    "text/csv",
    key='download-csv')

#Output to excel (only if openpyxl is installed - currently not installed)
st.write("TEST: below will not work because no openpyxl installed")
with pd.ExcelWriter('Sample downtime output 2021-22.xlsx') as writer:  
    df_av1_data.to_excel(writer, sheet_name='database')
    df_ts.to_excel(writer, sheet_name='DT Weight timeseries')
    df_ts_downtime.to_excel(writer, sheet_name='DT timeseries')
    df_ts_weight.to_excel(writer, sheet_name='Weight timeseries')

