import pandas as pd
import numpy as np
import streamlit as st

# Create a function to make the aggregate portfolio metrics
def create_port_metrics(metrics, comp_period):

    # Create a variable to hold the comparative period from the dropdown
    comparative_period = comp_period

    # Create a dict that has the comparative periods as keys, 
    # And the associated numbers to classify the EBEWE compliance date by LA building ID, as well as the starting year of the compliance period
    comp_dict = {'Dec 1, 2021: Comparative Period Jan 2016 - Dec 2020': [['0', '1'], 2016], 
                'Dec 1, 2022: Comparative Period Jan 2017 - Dec 2021': [['2', '3'], 2017], 
                'Dec 1, 2023: Comparative Period Jan 2018 - Dec 2022': [['4', '5'], 2018], 
                'Dec 1, 2024: Comparative Period Jan 2019 - Dec 2023': [['6', '7'], 2019], 
                'Dec 1, 2025: Comparative Period Jan 2020 - Dec 2024': [['8', '9'], 2020]}

    # Creating a dataframe to hold the metrics for the aggregated portfolio
    portfolio_metrics = pd.DataFrame()


    # Populate the first column of the portfolio metrics dataframe
    for year in range(comp_dict[comparative_period][1], comp_dict[comparative_period][1] + 5):
        # portfolio_metrics.loc[len(portfolio_metrics), 'Year Ending'] = f'{year}-12-31'
        portfolio_metrics.loc[len(portfolio_metrics), 'Year Ending'] = pd.to_datetime(f"{year}-{metrics['Year Ending'].dt.month.unique()[0]}-{metrics['Year Ending'].dt.day.unique()[0]}").strftime("%Y-%m-%d")

    # Populate the columns of the portfolio metrics df
    for year in portfolio_metrics['Year Ending'].unique():
        
        # Portfolio metrics
        # Get the energy use and ghg emissions totals and divide by the total square footage to get portfolio use/emissions intensity
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Portfolio Source EUI'] = round((
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Weather Normalized Source Energy Use (kBtu)'].sum() / 
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Property GFA - Self-Reported (ft²)'].sum()), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Portfolio GHG Emissions Intensity (kgCO2e/ft²)'] = round((
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Total (Location-Based) GHG Emissions (Metric Tons CO2e)'].sum() / 
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Property GFA - Self-Reported (ft²)'].sum()) * 1000, 2)
        
        # Energy Star Score percentile distribution columns
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Min'] = metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'].min()
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score 25th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 25), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Median'] = np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 50)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score 75th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 75), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Max'] = metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'].max()
        
        # Source EUI percentile distribution columns
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Min'] = metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'].min()
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI 25th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 25), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Median'] = np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 50)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI 75th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 75), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Max'] = metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'].max()

    # Format the integer columns within the portfolio_metrics dataframe
    int_cols = ['ES Score Min', 'ES Score 25th Percentile', 'ES Score Median', 
                'ES Score 75th Percentile', 'ES Score Max']

    # Removing the .0 from the values for exporting to excel
    for col in int_cols: 
        portfolio_metrics[col] = portfolio_metrics[col].astype(str).apply(lambda x: x.replace('.0', '')) 

    # Replace the string nans with actual NaNs    
    portfolio_metrics.replace('nan', np.nan, inplace = True)

    return portfolio_metrics