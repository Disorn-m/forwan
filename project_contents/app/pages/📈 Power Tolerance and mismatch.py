import os

import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, FormatStrFormatter,
                               MultipleLocator)

# FT_all=pd.read_csv(r"FR_645DEG21시리즈_20220111_PW_WIP.csv") ## Flast_Test Data Frame 330 W
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

st.set_page_config(layout="wide", page_title="📈 Power Tolerance and mismatch tool")
st.title("📈 Power Tolerance and Mismatch Tool")
st.markdown('This tool was prepared by Disorn Maneewongvatana and Chinnawat Pama. For more information please contact us.')
st.write('1. Please fill in the Solar PV benchmark form here https://forms.office.com/Pages/ResponsePage.aspx?id=xNC-oldZc0-wwqgRQHWQ--udlVQtMZlEthlijhw6yLpUQlA1STBUT0FSU0ZaSVBNUlpTN1kyVjBaQSQlQCN0PWcu.')
st.write('2. Please fill in flash test result into this CSV https://mottmac-my.sharepoint.com/:x:/p/d_maneewongvatana/Ecfl3LifyjhFgg5TaKRFxzgBGDSN3bf0xK0cArHM95mkGg?e=u2YYCE without changing the header.')


flashtest_files = st.file_uploader(
    "Please upload flash-test report", type=['csv'], accept_multiple_files=False)

Pmax = st.number_input(
    "Pmax (W)",
    key='Pmax_input')
col1, col2, col3 = st.columns(3)
with col1:
    Isc = st.number_input(
        "Isc (A)",
        key='Isc_input')
    Imp = st.number_input(
        "Imp (A)",
        key='Imp_input')
with col2:
    Voc = st.number_input(
        "Voc (V)",
        key='Voc_input')
    Vmp = st.number_input(
        "Vmp (V)",
        key='Vmp_input')
with col3:
    No_Modules_String = st.number_input(
        "Number of module per string",
        key='No_String_input',
        format="%d",
        step=1)
    Iterations = st.number_input(
        "Number of strings",
        key='Iterations_input',
        format="%d",
        step=1)

button = st.button("Calculate", )

def form_callback():
    st.session_state['callback'] = True


# Pmax=345 # For Power tolerance comparison
# Isc=9.46 #(A]For reference
# Voc=46.7 #(V]For reference
# Imp=9.04 #(A]For reference
# Vmp=38.2 #(V]For reference
# No_Modules_String=28 # As per PV plant design
# Iterations=9410 # Number of string for the module in the PV plant design


if button and flashtest_files is not None:
    df_flashTest_raw = pd.read_csv(flashtest_files)
    
    st.write(flashtest_files)
    #df_flashTest_raw = pd.read_csv(flashtest_files)
    st.header('Imported data')
    st.dataframe(df_flashTest_raw)

    df_flashTest = df_flashTest_raw[[
        'Voc(V)', 'Isc(A)', 'Pm(W)', 'Vpm(V)', 'Ipm(A)', 'Module ID']]  # Select useful columns
    # Rename columns to prefered names
    df_flashTest.columns = [
        'Voc(V)', 'Isc(A)', 'Pmax(W)', 'Vpm(V)', 'Ipm(A)', 'SN']

    # 1:: function to randomly select x number modules per string and calculate Power tolerance and mismatch
    
    def MismatchIter(num_iterations, modPerString, df_ft):
        It = []
        MMSt = []
        
        for i in range(0, num_iterations):
            # randomly selecting n modules
            It = df_ft.sample(n=modPerString).describe()
            It_Imp_min = It.loc['min', 'Ipm(A)']
            It_Isc_min = It.loc['min', 'Isc(A)']
            It_Imp_avg = It.loc['mean', 'Ipm(A)']
            It_Isc_avg = It.loc['mean', 'Isc(A)']
            MMLosses_Imp = (It_Imp_min-It_Imp_avg)/It_Imp_avg
            MMLosses_Isc = (It_Isc_min-It_Isc_avg)/It_Isc_avg
            df = pd.DataFrame([[It_Imp_min, It_Imp_avg, MMLosses_Imp, It_Isc_min, It_Isc_avg, MMLosses_Isc]], columns=[
                              'Imp_min', 'Imp_avg', 'MMLosses_Imp', 'Isc_min', 'Isc_avg', 'MMLosses_Isc'])
            if i == 0:
                MMSt = df
            else:
                MMSt = pd.concat([MMSt,df], ignore_index=True)
        return MMSt

    # 1:: function to assign number modules per string in order of the dataframe and calculate Power tolerance and mismatch
    st.header('String forming data - randomise')
    def get_mismatch_inOrder(ModperString, MM_list):

        df_data = MM_list.copy()
        df_data['str_num'] = np.divmod(np.arange(len(df_data)), ModperString)[
            0]+1  # Label each module to a string
        Ipm_min_inOrder = df_data.groupby('str_num')['Ipm(A)'].min()
        Ipm_avg_inOrder = df_data.groupby('str_num')['Ipm(A)'].mean()
        ImpMismatch_inOrder = (
            Ipm_min_inOrder - Ipm_avg_inOrder)/Ipm_avg_inOrder

        dict_results = {'Imp_min': Ipm_min_inOrder,
                        'Imp_avg': Ipm_avg_inOrder, 'I_mp_mismatch': ImpMismatch_inOrder}

        df_results_inOrder = pd.DataFrame(dict_results)
        df_results_inOrder

        return df_results_inOrder

    df_randomised_results = MismatchIter(
        Iterations, No_Modules_String, df_flashTest)
    st.write(df_randomised_results)

    # Average Isc and Imp of all the flash test data
    Average_module_Isc1 = df_flashTest.describe().loc['mean', 'Isc(A)']
    Average_module_Imp1 = df_flashTest.describe().loc['mean', 'Ipm(A)']

    # Average Isc and Imp of the randomised string forming
    Average_string_Isc1_min = np.mean(df_randomised_results['Isc_min'])
    Average_string_Imp1_min = np.mean(df_randomised_results['Imp_min'])

    # Mismatch on Imp
    ImpMismatch1 = (Average_string_Imp1_min-Average_module_Imp1) / \
        Average_module_Imp1  # Method 1
    avg_string_Imp1_mismatch = np.mean(
        df_randomised_results['MMLosses_Imp'])  # Method 2

    # Power tolerance
    PWTol1 = np.mean((df_flashTest['Pmax(W)']-Pmax)/Pmax)
    # Combined power tolerance and missmatch
    C_PWtol_MM1 = ((1+PWTol1)*(1+ImpMismatch1))-1

    # Display results
    st.header("Randomised string forming for %d iterations" % Iterations)
    st.write("Power Tolerance based on P Max: ")
    st.write(str(round(PWTol1*100, 4))+"%")
    st.write("Mismatch based on Imp method#1 with average of string's Ipm_min: ")
    st.write(str(round(ImpMismatch1*100, 4))+"%")
    st.write("Mismatch based on Imp method#2 with average of string's %Ipm_mismatch: ")
    st.write(str(round(avg_string_Imp1_mismatch*100, 4))+"%")
    st.write("Combined power tolareance and mismatch: ")
    st.write(str(round(C_PWtol_MM1*100, 4))+"%")

    # plot
    fig, ax = plt.subplots(figsize=(20, 7))
    ax.scatter(df_randomised_results.index,
               df_randomised_results['MMLosses_Imp'])
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Imp Mismatch%')
    ax.set_title('Randomised string forming')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.00))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True)

    # Plot the average line'
    y_mean = [np.mean(df_randomised_results['MMLosses_Imp'])] * \
        len(df_randomised_results.index)
    mean_line = ax.plot(df_randomised_results.index, y_mean,
                        label='Mean', color='red', linestyle='--')
    ax.annotate("{:.3%}".format(avg_string_Imp1_mismatch), (0, y_mean[0]))

    st.pyplot(fig)

    # plot
    fig = plt.figure(1, (20, 7))
    plt.scatter(df_randomised_results.index,
                df_randomised_results['MMLosses_Imp'], label="%mismatch")
    plt.xlabel('Iteration')
    plt.ylabel('Mismatch')
    plt.title('Randomised string forming')
    plt.legend()

    # after plotting the data, format the labels
    current_values = plt.gca().get_yticks()
    # using format string '{:.0f}' here but you can choose others
    plt.gca().set_yticklabels(['{:,.2%}'.format(x) for x in current_values])







    st.header('String forming data - ordered')
    df_runInOrder_results = get_mismatch_inOrder(
        No_Modules_String, df_flashTest)
    df_runInOrder_results.head()

    # Average Isc and Imp of all the flash test data
    Average_module_Isc1 = df_flashTest.describe().loc['mean', 'Isc(A)']
    Average_module_Imp1 = df_flashTest.describe().loc['mean', 'Ipm(A)']

    # Average Imp of the InOrder string forming
    Average_string_Imp1_min_inOrder = np.mean(df_runInOrder_results['Imp_min'])

    # Mismatch on Imp
    ImpMismatch1_inOrder = (Average_string_Imp1_min_inOrder -
                            Average_module_Imp1)/Average_module_Imp1  # Method 1
    avg_string_Imp1_mismatch_inOrder = np.mean(
        df_runInOrder_results['I_mp_mismatch'])  # Method 2

    # Power tolerance
    PWTol1 = np.mean((df_flashTest['Pmax(W)']-Pmax)/Pmax)
    # Combined power tolerance and missmatch
    C_PWtol_MM1 = ((1+PWTol1)*(1+ImpMismatch1_inOrder))-1

    # Display results
    st.header("Ordered string forming for %d strings" % len(df_runInOrder_results.index))
    st.write("Power Tolerance based on P Max: ")
    st.write(str(round(PWTol1*100, 4))+"%")
    st.write("Mismatch based on Imp method#1 with average of string's Ipm_min: ")
    st.write(str(round(ImpMismatch1_inOrder*100, 4))+"%")
    st.write("Mismatch based on Imp method#2 with average of string's %Ipm_mismatch: ")
    st.write(str(round(avg_string_Imp1_mismatch_inOrder*100, 4))+"%")
    st.write("Combined power tolareance and mismatch: ")
    st.write(str(round(C_PWtol_MM1*100, 4))+"%")

    # plot
    fig, ax = plt.subplots(figsize=(20, 7))
    ax.scatter(df_runInOrder_results.index,
               df_runInOrder_results['I_mp_mismatch'])
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Imp Mismatch%')
    ax.set_title('String forming')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.00))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True)

    # Plot the average line'
    y_mean_inOrder = [np.mean(
        df_runInOrder_results['I_mp_mismatch'])]*len(df_runInOrder_results.index)
    mean_line_inOrder = ax.plot(df_runInOrder_results.index,
                                y_mean_inOrder, label='Mean', color='red', linestyle='--')
    ax.annotate("{:.3%}".format(avg_string_Imp1_mismatch_inOrder),
                (0, y_mean_inOrder[0]))

    st.pyplot(fig)
else:
    st.error('Please upload the files and fill the required fields then click "Calculate"') 


