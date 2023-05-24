from plotly.offline import init_notebook_mode, iplot
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

import chart_studio.plotly as py
import plotly.graph_objs as go
import io
# Display all cell outputs
from IPython.core.interactiveshell import InteractiveShell

InteractiveShell.ast_node_interactivity = 'all'

# Visualization

plt.style.use('bmh')

# Offline mode

init_notebook_mode(connected=True)


def info(X):
    buffer = io.StringIO()
    X.info(buf=buffer)
    s = buffer.getvalue()
    st.write(s)


st.set_page_config(layout="wide", page_title="💹 Graph plotter")
st.title("💹 Graph plotter")
st.markdown(
    'This tool was prepared by Disorn Maneewongvatana. For more information please contact us.'
)

filename = st.file_uploader("Please upload file",
                            type=['csv'],
                            accept_multiple_files=False)

graph_title = st.text_input('Graph title', 'Graph title')
Col1, Col2, Col3 = st.columns(3)
with Col1:
    No_Value = st.number_input('Please enter the number of variable to show',
                               min_value=1,
                               max_value=5,
                               value=1,
                               step=1)

with Col2:
    Datetime_format = st.text_input('Please input datetime format', placeholder='e.g. %Y/%m/%d %H:%M',
                                    help='%d = day, %m = month, %Y = year, %H = hour, %M = minute. e.g. "%d/%m/%Y %H:%M"')

with Col3:
    Fixed_range = st.radio('fixed Y-axis range',
                           (True, False), key='fixed range')

Col1, Col2 = st.columns(2)
with Col1:
    left_axis = st.text_input('Please enter the left axis name',
                              'e.g. Irradiation')
with Col2:
    right_axis = st.text_input('Please enter the right axis name',
                               'e.g. Energy')

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    value_1_name = st.text_input("Column 1 name",
                                 key='Column 1 name',
                                 placeholder='Required')
    value_1_axies = st.radio('axies', ('Left', 'Right'), key='Column 1 axies')

with col2:
    value_2_name = st.text_input("Column 2 name",
                                 key='Column 2 name',
                                 placeholder='leave blank if not applicable')
    value_2_axies = st.radio('axies', ('Left', 'Right'), key='Column 2 axies')

with col3:
    value_3_name = st.text_input("Column 3 name",
                                 key='Column 3 name',
                                 placeholder='leave blank if not applicable')
    value_3_axies = st.radio('axies', ('Left', 'Right'), key='Column 3 axies')

with col4:
    value_4_name = st.text_input("Column 4 name",
                                 key='Column 4 name',
                                 placeholder='leave blank if not applicable')
    value_4_axies = st.radio('axies', ('Left', 'Right'), key='Column 4 axies')

with col5:
    value_5_name = st.text_input("Column 5 name",
                                 key='Column 5 name',
                                 placeholder='leave blank if not applicable')
    value_5_axies = st.radio('axies', ('Left', 'Right'), key='Column 5 axies')


if value_1_axies == 'Left':
    value_1_axies = 'y'
else:
    value_1_axies = 'y2'
if value_2_axies == 'Left':
    value_2_axies = 'y'
else:
    value_2_axies = 'y2'
if value_3_axies == 'Left':
    value_3_axies = 'y'
else:
    value_3_axies = 'y2'
if value_4_axies == 'Left':
    value_4_axies = 'y'
else:
    value_4_axies = 'y2'
if value_5_axies == 'Left':
    value_5_axies = 'y'
else:
    value_5_axies = 'y2'

# Read in data and convert index to a datetime
button = st.button("Plot", )

if button and filename is not None:

    if value_1_name == '':

        st.error('Please enter the name of the Column')

    elif No_Value >= 2 and (value_2_name == ''):

        st.error('Please enter the name of the Column')
    elif No_Value >= 3 and ((value_3_name or value_2_name or value_1_name)
                            == ''):

        st.error('Please enter the name of the Column')
    elif No_Value >= 4 and ((value_4_name or value_3_name or value_2_name
                             or value_1_name) == ''):

        st.error('Please enter the name of the Column')
    elif No_Value >= 5 and ((value_5_name or value_4_name or value_3_name
                             or value_2_name or value_1_name) == ''):

        st.error('Please enter the name of the Column')

    df = pd.read_csv(filename)

    df.rename(columns={df.columns[0]: 'Datetime'})
    df['Datetime'] = pd.to_datetime(df['Datetime'],
                                    format=Datetime_format,
                                    )
    df.sort_index(inplace=True)
    df = df.set_index(df.columns[0])

    value_1 = df.loc[:, df.columns[0]]
    try:
        value_2 = df.loc[:, df.columns[1]]
    except:
        pass
    try:
        value_3 = df.loc[:, df.columns[2]]
    except:
        pass
    try:
        value_4 = df.loc[:, df.columns[3]]
    except:
        pass
    try:
        value_5 = df.loc[:, df.columns[4]]
    except:
        pass

    value_1_graph = go.Scatter(x=value_1.index,
                               y=value_1.values,
                               line=dict(color='red', width=3),
                               opacity=0.8,
                               name=value_1_name,
                               yaxis=value_1_axies,
                               text=[f'{x:.1f}' for x in value_1.values])

    try:
        value_2_graph = go.Scatter(x=value_2.index,
                                   y=value_2.values,
                                   line=dict(color='blue', width=3),
                                   opacity=0.8,
                                   name=value_2_name,
                                   yaxis=value_2_axies,
                                   text=[f'{x:.1f}' for x in value_2.values])
    except:
        pass
    try:
        value_3_graph = go.Scatter(x=value_3.index,
                                   y=value_3.values,
                                   line=dict(color='green', width=3),
                                   opacity=0.8,
                                   name=value_3_name,
                                   yaxis=value_3_axies,
                                   text=[f'{x:.1f}' for x in value_3.values])
    except:
        pass
    try:
        value_4_graph = go.Scatter(x=value_4.index,
                                   y=value_4.values,
                                   line=dict(color='yellow', width=3),
                                   opacity=0.8,
                                   name=value_4_name,
                                   yaxis=value_4_axies,
                                   text=[f'{x:.1f}' for x in value_4.values])
    except:
        pass
    try:
        value_5_graph = go.Scatter(x=value_5.index,
                                   y=value_5.values,
                                   line=dict(color='orange', width=3),
                                   opacity=0.8,
                                   name=value_5_name,
                                   yaxis=value_5_axies,
                                   text=[f'{x:.1f}' for x in value_5.values])
    except:
        pass

    if No_Value == 1:
        data = [value_1_graph]
    elif No_Value == 2:
        data = [value_1_graph, value_2_graph]
    elif No_Value == 3:
        data = [value_1_graph, value_2_graph, value_3_graph]
    elif No_Value == 4:
        data = [value_1_graph, value_2_graph, value_3_graph, value_4_graph]
    elif No_Value == 5:
        data = [
            value_1_graph, value_2_graph, value_3_graph, value_4_graph,
            value_5_graph
        ]

    layout = go.Layout(
        height=800,
        width=1500,
        title=graph_title,
        xaxis=dict(
            title='Date',
            # Range selector with buttons
            rangeselector=dict(
                # Buttons for selecting time scale
                buttons=list([
                    # 1 month
                    dict(
                        count=1,
                        label='1m',
                        step='month',
                        stepmode='backward',
                    ),
                    # 1 week
                    dict(count=7, label='1w', step='day', stepmode='todate'),
                    # 1 day
                    dict(count=1, label='1d', step='day', stepmode='todate'),
                    # 12 hours
                    dict(count=12,
                         label='12h',
                         step='hour',
                         stepmode='backward'),
                    # 4 hours
                    dict(count=4, label='4h', step='hour', stepmode='backward'
                         ),
                    # Entire scale
                    dict(step='all')
                ])),
            # Sliding for selecting time window
            rangeslider=dict(visible=True),
            # Type of xaxis
            type='date'),
        yaxis=dict(title=left_axis,
                   autorange=True,
                   fixedrange=Fixed_range,
                   side='left'),
        # Add a second yaxis to the right of the plot
        yaxis2=dict(title=right_axis,
                    autorange=True,
                    fixedrange=Fixed_range,
                    overlaying='y',
                    side='right'),
        plot_bgcolor='white',
        font=dict(size=20),
        legend_x=1.1
    )

    fig = go.Figure(data, layout=layout)
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeselector_font_color='black',
        xaxis_rangeselector_activecolor='red',
        xaxis_rangeselector_bgcolor='green',
    )
    st.plotly_chart(fig, use_container_width=True)

    buffer = io.StringIO()
    fig.write_html(buffer, include_plotlyjs='cdn')
    html_bytes = buffer.getvalue().encode()

    st.download_button(label='Download graph as HTML',
                       data=html_bytes,
                       file_name=graph_title + '.html',
                       mime='text/html')
else:
    st.error(
        'Please upload the files and fill the required fields then click "Calculate"'
    )
