import streamlit as st
import pandas as pd
from Utilities.clean_metrics import clean_metrics
from Utilities.create_compliance import create_compliance
from Utilities.create_port_df import create_port_df
from Utilities.top_quartile_SEUI import top_quartile_SEUI
from Utilities.bottom_quartile_SEUI import bottom_quartile_SEUI
from Utilities.create_port_metrics import create_port_metrics
from Utilities.create_workbook import create_workbook



# Create a title and instructions
st.title('Benchmarking and EBEWE Compliance Analytics')
st.sidebar.markdown('''
    <h1>Notes:</h1>
    Use the following instructions to create a report in ESPM and export it as an excel workbook. Select the compliance period from the dropdown and upload the ESPM report.

    - Creating the ESPM report:
        - Timeframe: Date Range
            - Yearly for the chosen compliance period.
            - For example: Compliance due date Dec 1, 2022:
                - Choose yearly from Dec 31, 2017 to Dec 31, 2021
            
        - Properties 
            - Select which buildings to include in the report

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
        ''', unsafe_allow_html = True)

# Display a select box
comp_period = st.selectbox('Choose an EBEWE Compliance Year', ['Dec 1, 2021: Comparative Period Jan 2016 - Dec 2020', 
                                                                'Dec 1, 2022: Comparative Period Jan 2017 - Dec 2021', 
                                                                'Dec 1, 2023: Comparative Period Jan 2018 - Dec 2022', 
                                                                'Dec 1, 2024: Comparative Period Jan 2019 - Dec 2023', 
                                                                'Dec 1, 2025: Comparative Period Jan 2020 - Dec 2024'])


espm_report = st.file_uploader('Upload ESPM Report')

if espm_report is not None:

    # Create a dataframe from the uploaded file
    espm_data = pd.read_excel(espm_report, 
                            skiprows = 5)

    # Clean the metrics df
    metrics = clean_metrics(espm_data)

    # Create the compliance 2021 data
    compliance_data = create_compliance(metrics, comp_period)

    # Create porfolio df (individual buildings)
    portfolio_df = create_port_df(metrics, comp_period)

    # Create best eui shifts df
    best_eui_shifts = top_quartile_SEUI(portfolio_df, comp_period)

    # Create worst eui shifts df
    worst_eui_shifts = bottom_quartile_SEUI(portfolio_df, comp_period)

    # Create Portfolio Metrics df (as an aggregate portfolio)
    portfolio_metrics = create_port_metrics(metrics, comp_period)

    # Create a download button for the processed dataframes
    workbook = create_workbook(portfolio_metrics, portfolio_df, compliance_data, best_eui_shifts, worst_eui_shifts, comp_period)
    
    st.download_button(label = 'Download Porfolio Analytics Workbook', 
                        data = workbook,
                        file_name = 'Portfolio Benchmarking Analytics.xlsx')

