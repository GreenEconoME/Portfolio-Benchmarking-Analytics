import streamlit as st
import pandas as pd
import numpy as np
from Utilities.transformation_functions import (clean_metrics, 
                                                create_compliance_21, 
                                                create_port_df, 
                                                top_quartile_SEUI, 
                                                bottom_quartile_SEUI, 
                                                create_port_metrics, 
                                                create_workbook)

# Create a title and instructions
st.title('2022 Compliance Year')
st.subheader('Benchmarking and EBEWE Compliance Analytics')
st.markdown('''
    - Notes:
        - 2022 compliance date is for LADBS Building IDs that end in 2 or 3
        - Comparative period is 2017 - 2021

    - To create the report  
    - Timeframe: Date Range
        - Yearly from Dec 31, 2017 to Dec 31st 2021
        
    - Properties 
        - Select which building to include in the report

    - Information and Metrics
        - Los Angeles Building ID
        - Energy Star Score
        - Weather Normalized Source EUI (kBtu/sqft)
        - Weather Normalized Source Energy Use (kBtu)
        - National Median Source EUI (kBtu/sqft)
        - Total GHG Emissions Intensity (kgCO2e/sqft)
        - Total GHG Emissions (Metric Tons CO2e)
        - Property GFA - Self-Reported (sqft)
        - Water Use Intensity (All Water Sources) (gal/sqft)
        ''')

espm_report = st.file_uploader('Upload ESPM Report')

if espm_report is not None:

    # Create a dataframe from the uploaded file
    espm_data = pd.read_excel(espm_report, 
                            skiprows = 5)

    # Clean the metrics df
    metrics = clean_metrics(espm_data)

    # Create the compliance 2021 data
    compliance_data_21 = create_compliance_21(metrics)

    # Create porfolio df (individual buildings)
    portfolio_df = create_port_df(metrics)

    # Create best eui shifts df
    best_eui_shifts = top_quartile_SEUI(portfolio_df)

    # Create worst eui shifts df
    worst_eui_shifts = bottom_quartile_SEUI(portfolio_df)

    # Create Portfolio Metrics df (as an aggregate portfolio)
    portfolio_metrics = create_port_metrics(metrics)

    # Create a download button for the processed dataframes
    workbook = create_workbook(portfolio_metrics, portfolio_df, compliance_data_21, best_eui_shifts, worst_eui_shifts)
    
    st.download_button(label = 'Download Porfolio Analytics Workbook', 
                        data = workbook,
                        file_name = 'Portfolio Benchmarking Analytics.xlsx')

