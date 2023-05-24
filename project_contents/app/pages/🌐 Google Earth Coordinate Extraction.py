import pandas as pd
import geopandas as gpd
import os
import glob
import numpy as np
import io
import fiona
import streamlit as st

st.set_page_config(layout="wide",
                   page_title="🌐 Google Earth Coordinate Extraction")
st.title("🌐 Google Earth Coordinate Extraction")
st.markdown(
    'This tool was prepared by Chaiyanun Watcharapichitchai, Disorn Maneewongvatana and Chinnawat Pama. For more information please contact us.'
)

#instruction
st.write(
    'Instruction: Save your working placemark in Google Earth file as <.kml> file'
)
st.write(
    'Please note that this tool only works with KML that only has placemark (pins) only with no lines or polygons'
)

fiona.drvsupport.supported_drivers['kml'] = 'rw'  # enable KML support
fiona.drvsupport.supported_drivers['KML'] = 'rw'

#File = r'C:\Users\WAT98674\Downloads\TEST.kml'
File = st.file_uploader("Please upload <.kml> file",
                        type=['kml'],
                        accept_multiple_files=False)

#File = r'C:\Users\WAT98674\Downloads\TEST.csv'

if File is not None:

    df = gpd.read_file(File)

    df['long'] = df['geometry'].x
    df['lat'] = df['geometry'].y
    df = df.loc[:, ["Name", "long", "lat"]]

    st.write(df)

    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

    st.download_button(label="Press to Download .CSV",
                       data=csv,
                       file_name='coordinate.csv',
                       mime="text/csv",
                       key='download-csv')
