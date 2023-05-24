import pandas as pd
import os
import glob
import numpy as np
import streamlit as st
import io

st.set_page_config(layout="wide",
                   page_title="🌞 Combine Irradiation data from PVsyst")
st.title('Combine Irradiation data from PVsyst')

col1, col2 = st.columns(2)
with col1:
    IRR_files = st.file_uploader("Please upload PVsyst output file",
                                 type=['csv'],
                                 accept_multiple_files=True)

with col2:
    Area_file = st.file_uploader("Please upload Area file",
                                 type=['csv'],
                                 accept_multiple_files=False)

# location of the batch file (see example for expect format)
#batch_loc = r"C:\Users\MAN94035\Desktop\Banshu batch\raw"
# location of the area file (see example for expect format)
#area_loc = r"C:\Users\MAN94035\Desktop\Banshu batch\area"
# the name of the file
area = 'area.csv'
# location of the result file
#result_loc = r"C:\Users\MAN94035\Desktop\Banshu batch"
# Name pattern - to identify the numbering (see example input)
pattern = "Banshu_SIM(\w+)"
# number of rows before irradiation data include blank and heading in the csv file
g = 13
# number of blank row in the csv file
o = 3
# result file name
result_name = 'Results_Banshu_batch.csv'

pattern = st.text_input(
    'Name pattern - to identify the numbering (see example input)',
    'Banshu_SIM(\w+)')

button = st.button("Calculate", )



NO_files = len(IRR_files)
st.write('Number of files: ', NO_files)




if button and IRR_files and Area_file is not None:
    my_bar = st.progress(0)
    progress = 0
    # reading area array
    area_ar = pd.read_csv(Area_file)
    a = pd.DataFrame(area_ar)
    # area_np=np.array(area_ar)


    import re
    cut = g - o
    fo = ".csv"
    i = 0
    f = 0
    s_int = []
    s_str = []
    ss_str = []
    real_name = []
    df = pd.DataFrame()
    df2 = pd.DataFrame()
    area = pd.DataFrame()
    pattern2 = pattern.split('(\w+)')[0]
    
    numbers = st.empty()

    for names in IRR_files:
        Com = 1/(NO_files)
        progress = progress+Com
        pro = round(progress,2)
        try:
            my_bar.progress(pro)
        except:
            pass

        with numbers.container():
            st.write(pro*100, '%')

        column_name = names.name.split('.')[0]
        column_name = column_name.split(pattern2)[1]
        column_name = int(column_name)
        
        data = pd.read_csv(names,
                           encoding='cp1252',
                           index_col=None,
                           header=None,
                           error_bad_lines=False)
        data_cut = pd.DataFrame(data[cut:])
        data_cut.columns = ['bada']
        data_de = data_cut.bada.str.split(';', expand=True)
        data_de.columns = ['datetime', column_name]
        # set index to date time
        df_GII = data_de.set_index('datetime')
        
        
        
        df = pd.concat([df,df_GII],axis=1)
    df = df.reindex(sorted(df.columns), axis=1)    
    st.write(df)
    
    Area_file.seek(0)
    area = pd.read_csv(Area_file,index_col=None,
                       error_bad_lines=False)
    
    Total_area = area.sum()
    Total_area = float(Total_area)  
    area2 = area/Total_area
    area2.insert(0,'column',range(1,1+len(area_ar)))
    area2.insert(0,'index','a')
    area3 = area2.pivot(index='index',columns='column',values='area' )
    area3 = area3.astype(dtype='float64')
    df = df.astype(dtype='float64')
    #st.write(area3.info)

  

    for col in np.arange(0,df.shape[1]):
        df.iloc[:,col]=df.iloc[:,col]*area3.iloc[0,col]    

    df = df.sum(axis=1)
    
    df = df.reset_index()
    df = df.rename(columns={df.columns[1]: "IRR"})
   

    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')


    csv = convert_df(df)
   
     


    st.download_button(
    "Press to Download",
    csv,
    "combine " + pattern2 + " IRR.csv",
    "text/csv",
    key='download-csv')

else:
    st.error('Please upload the files and fill the required fields then click "Calculate"') 