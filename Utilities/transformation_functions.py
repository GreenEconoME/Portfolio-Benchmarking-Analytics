import numpy as np
import streamlit as st
import pandas as pd
from io import BytesIO

# Defining a helper function to find the min of a list of tuples based on first element of tuple, and return the second value of tuple
def filter_tuple_list(given_list, target_value):
    for x, y in given_list:
        if x == target_value:
            return y

# Create function to clean initial ESPM export
def clean_metrics(metrics):

    # Remove parent columns - contain no data but come with download
    metrics.drop(columns = ['Parent Property Id', 'Parent Property Name'], inplace = True)

    # Replace Not Available with NaN values, remove leading and trailing zeros from building ID
    metrics.replace('Not Available', np.nan, inplace = True)
    metrics['Los Angeles Building ID'] = metrics['Los Angeles Building ID'].astype(str).str.strip()

    return metrics

# Create the 2022 compliance year EBEWE data
def create_compliance_21(metrics):
    # Getting the rows that contain properties that need to comply in 2022 (2017 - 2021 comparative period)
    compliance_2021 = []
    for row in metrics.index:
        if not pd.isnull(metrics.loc[row, 'Los Angeles Building ID']):
            if metrics.loc[row, 'Los Angeles Building ID'][-1] in ['2', '3']:
                compliance_2021.append(row)


    # Creating a dataframe to hold the EBEWE data for buildings with 2021 compliance year
    data = []
    for prop in metrics.loc[compliance_2021, 'Property Name'].unique():
        # Create and populate a dictionary to hold each properties information
        prop_info = {}
        prop_info['ESPM Property Id'] = metrics.loc[metrics['Property Name'] == prop, 'Property Id'].values[0]
        prop_info['Property Name'] = prop
        prop_info['LA Building Id'] = metrics.loc[metrics['Property Name'] == prop, 'Los Angeles Building ID'].values[0]
        prop_info['Square Footage'] = metrics.loc[metrics['Property Name'] == prop, 'Property GFA - Self-Reported (ft²)'].values[0]
        
        # Append the property information dictionary to the list of data
        data.append(prop_info)
        
    # Create a dataframe from each properties information
    compliance_data_21 = pd.DataFrame(data)
    
    # Check if df is empty - will happen if no buildings have an LA Building ID
    if not compliance_data_21.empty:

        # Populating the 2017 - 2021 EBEWE Compliance comparative period data   
        for row in compliance_data_21.index:
            
            # Populate the comparative period's Energy Star Score
            for year in range(2017, 2022):
                compliance_data_21.loc[row, f'{year} ES Score'] = metrics.loc[(metrics['Property Id'] == compliance_data_21.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'ENERGY STAR Score'].item()
                
            # Populate the comparative period's Source EUI
            for year in range(2017, 2022):
                compliance_data_21.loc[row, f'{year} Weather Normalized Source EUI'] = metrics.loc[(metrics['Property Id'] == compliance_data_21.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Weather Normalized Source EUI (kBtu/ft²)'].item()
                
            # Populate the comparative period's Water UI
            for year in range(2017, 2022):
                compliance_data_21.loc[row, f'{year} Water UI'] = metrics.loc[(metrics['Property Id'] == compliance_data_21.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Water Use Intensity (All Water Sources) (gal/ft²)'].item()
            
            # Populate the 2021 National Median Source EUI column
            compliance_data_21.loc[row, '2021 National Median Source EUI'] = metrics.loc[(metrics['Property Id'] == compliance_data_21.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == '2021-12-31'), 'National Median Source EUI (kBtu/ft²)'].item()
            
            # Populate the comparative period's Best Source EUI % Change
            # Create a list to hold the percent changes for each year
            eui_percent_changes = []
            for year in range(2017, 2021):
                if pd.notnull(compliance_data_21.loc[row, f'{year} Weather Normalized Source EUI']):
                    eui_percent_changes.append(((compliance_data_21.loc[row, '2021 Weather Normalized Source EUI'] - compliance_data_21.loc[row, f'{year} Weather Normalized Source EUI']) / compliance_data_21.loc[row, f'{year} Weather Normalized Source EUI'], year))
            # Set the Best EUI % Reduction value to the best percent change
            if len(eui_percent_changes) != 0:
                compliance_data_21.loc[row, 'Best EUI % Reduction'] = round(min(eui_percent_changes, key = lambda x: x[0])[0] * 100, 2)
                # Populate the Comparative Year of Best Source EUI % Change
                compliance_data_21.loc[row, 'Best EUI % Reduction Year'] = filter_tuple_list(eui_percent_changes, min(eui_percent_changes, key = lambda x: x[0])[0])
            
            # Populate the Energy Exemption #1 column
            if compliance_data_21.loc[row, '2021 ES Score'] >= 75:
                compliance_data_21.loc[row, 'Energy Exemption #1?'] = 'Possible'
            else:
                compliance_data_21.loc[row, 'Energy Exemption #1?'] = 'No'        
            
            # Populate the Energy Exemption #4 column
            if compliance_data_21.loc[row, 'Best EUI % Reduction'] <= -15: 
                compliance_data_21.loc[row, 'Energy Exemption #4?'] = 'Yes'
            else:
                compliance_data_21.loc[row, 'Energy Exemption #4?'] = 'No'
                
            # Populate the comparative period's Best Water UI % Change
            # Create a list to hold the percent changes for each year
            wui_percent_changes = []
            for year in range(2017, 2021):
                if pd.notnull(compliance_data_21.loc[row, f'{year} Water UI']):
                    wui_percent_changes.append(((compliance_data_21.loc[row, '2021 Water UI'] - compliance_data_21.loc[row, f'{year} Water UI']) / compliance_data_21.loc[row, f'{year} Water UI'], year))
            # Set the Best Water UI % Reduction value to the best percent change
            if len(wui_percent_changes) != 0:
                compliance_data_21.loc[row, 'Best Water UI % Change'] = round(min(wui_percent_changes, key = lambda x: x[0])[0] * 100, 2)
                # Populate the Best Water UI % Reduction Year column
                compliance_data_21.loc[row, 'Best Water UI % Change Year'] = filter_tuple_list(wui_percent_changes, min(wui_percent_changes, key = lambda x: x[0])[0])
            
            # Populate the Water Exemption #1 column
            if compliance_data_21.loc[row, 'Best Water UI % Change'] <= -20:
                compliance_data_21.loc[row, 'Water Exemption #1?'] = 'Yes'
            else:
                compliance_data_21.loc[row, 'Water Exemption #1?'] = 'No'

        # Format the compliance_data_21 dataframe
        int_cols = ['Square Footage', '2017 ES Score', '2018 ES Score', 
                    '2019 ES Score', '2020 ES Score', '2021 ES Score', 
                    'Best EUI % Reduction Year', 'Best Water UI % Change Year']
        for col in int_cols: 
            compliance_data_21[col] = compliance_data_21[col].astype(str).apply(lambda x: x.replace('.0', '')) 
            
        compliance_data_21.replace('nan', np.nan, inplace = True)

    return compliance_data_21

# Create function to make benchmarking metrics for full portfolio
def create_port_df(metrics):
    # Creating a dataframe to hold the portfolio data for buildings
    data = []
    for prop in metrics['Property Name'].unique():
        # Create and populate a dictionary to hold each properties information
        prop_info = {}
        prop_info['ESPM Property Id'] = metrics.loc[metrics['Property Name'] == prop, 'Property Id'].values[0]
        prop_info['Property Name'] = prop
        prop_info['LA Building Id'] = metrics.loc[metrics['Property Name'] == prop, 'Los Angeles Building ID'].values[0]
        prop_info['Square Footage'] = metrics.loc[metrics['Property Name'] == prop, 'Property GFA - Self-Reported (ft²)'].values[0]
        
        # Append the property information dictionary to the list of data
        data.append(prop_info)
        
    # Create a dataframe from each properties information
    portfolio_df = pd.DataFrame(data)

    # Populating the 2017 - 2021 EBEWE Compliance comparative period data
    for row in portfolio_df.index:
        
        # Populate the last three years Energy Star Score
        for year in range(2019, 2022):
            portfolio_df.loc[row, f'{year} ES Score'] = metrics.loc[(metrics['Property Id'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'ENERGY STAR Score'].item()
            
        # Populate the last three years Source EUI
        for year in range(2019, 2022):
            portfolio_df.loc[row, f'{year} Weather Normalized Source EUI'] = metrics.loc[(metrics['Property Id'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Weather Normalized Source EUI (kBtu/ft²)'].item()
            
        # Populate the last three years Water UI
        for year in range(2019, 2022):
            portfolio_df.loc[row, f'{year} Water UI'] = metrics.loc[(metrics['Property Id'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Water Use Intensity (All Water Sources) (gal/ft²)'].item()
        
        # Populate the GHG Emissions Intensity for 2021
        portfolio_df.loc[row, '2021 Total GHG Emissions Intensity (kgCO2e/ft²)'] = metrics.loc[(metrics['Property Id'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == '2021-12-31'), 'Total GHG Emissions Intensity (kgCO2e/ft²)'].item()
        # Populate the 2021 National Median Source EUI column
        portfolio_df.loc[row, '2021 National Median Source EUI'] = metrics.loc[(metrics['Property Id'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == '2021-12-31'), 'National Median Source EUI (kBtu/ft²)'].item()
        
        # Populate the 2021 % difference from National Source EUI
        portfolio_df.loc[row, '2021 % Difference From National Source EUI'] = round(((portfolio_df.loc[row, '2021 Weather Normalized Source EUI'] - portfolio_df.loc[row, '2021 National Median Source EUI']) / portfolio_df.loc[row, '2021 National Median Source EUI']) * 100, 2)
        
        # Populate the Source EUI % Change from 2020 to 2021
        portfolio_df.loc[row, '2020-2021 EUI % Change'] = round(((portfolio_df.loc[row, '2021 Weather Normalized Source EUI'] - portfolio_df.loc[row, '2020 Weather Normalized Source EUI']) / portfolio_df.loc[row, '2020 Weather Normalized Source EUI']) * 100, 2)
            
        # Populate the 2020 - 2021 Water UI % Change
        portfolio_df.loc[row, '2020-2021 Water UI % Change'] = round(((portfolio_df.loc[row, '2021 Water UI'] - portfolio_df.loc[row, '2020 Water UI']) / portfolio_df.loc[row, '2020 Water UI']) * 100, 2)
    
    # Format the portfolio_df dataframe
    int_cols = ['Square Footage', '2019 ES Score', 
                '2020 ES Score', '2021 ES Score']

    for col in int_cols: 
        portfolio_df[col] = portfolio_df[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
    portfolio_df.replace('nan', np.nan, inplace = True)

    return portfolio_df

# Create a function to make the top quartile for Source EUI Change
def top_quartile_SEUI(portfolio_df):
    best_eui_shifts = portfolio_df.loc[portfolio_df['2020-2021 EUI % Change'] <= np.nanpercentile(portfolio_df['2020-2021 EUI % Change'], 25)]
    best_eui_shifts.sort_values(by = '2020-2021 EUI % Change', inplace = True)

    # Format the best_eui_shifts dataframe
    int_cols = ['Square Footage', '2019 ES Score', 
                '2020 ES Score', '2021 ES Score']

    for col in int_cols: 
        best_eui_shifts[col] = best_eui_shifts[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
    best_eui_shifts.replace('nan', np.nan, inplace = True)

    return best_eui_shifts

# Create a function to make the bottom quartile for Source EUI Change
def bottom_quartile_SEUI(portfolio_df):
    worst_eui_shifts = portfolio_df.loc[portfolio_df['2020-2021 EUI % Change'] >= np.nanpercentile(portfolio_df['2020-2021 EUI % Change'], 75)]
    worst_eui_shifts.sort_values(by = '2020-2021 EUI % Change', ascending = False, inplace = True)

    # Format the worst_eui_shifts dataframe
    int_cols = ['Square Footage', '2019 ES Score', 
                '2020 ES Score', '2021 ES Score']

    for col in int_cols: 
        worst_eui_shifts[col] = worst_eui_shifts[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
    worst_eui_shifts.replace('nan', np.nan, inplace = True)

    return worst_eui_shifts

# Create a function to make the aggregate portfolio metrics
def create_port_metrics(metrics):
    # Creating a dataframe to hold the metrics for the aggregated portfolio
    portfolio_metrics = pd.DataFrame()

    # Populate the first column of the portfolio metrics dataframe
    for year in range(2017, 2022):
        portfolio_metrics.loc[len(portfolio_metrics), 'Year Ending'] = f'{year}-12-31'

    # Populate the columns of the portfolio metrics df
    for year in portfolio_metrics['Year Ending'].unique():
        
        # Portfolio metrics
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Portfolio Source EUI'] = round((
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Weather Normalized Source Energy Use (kBtu)'].sum() / 
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Property GFA - Self-Reported (ft²)'].sum()), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Portfolio GHG Emissions Intensity (kgCO2e/ft²)'] = round((
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Total GHG Emissions (Metric Tons CO2e)'].sum() / 
            metrics.loc[(~metrics['Weather Normalized Source Energy Use (kBtu)'].isna()) & (metrics['Year Ending'] == year), 'Property GFA - Self-Reported (ft²)'].sum()) * 1000, 2)
        
        # Energy Star Score Distribution Columns
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Min'] = metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'].min()
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score 25th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 25), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Median'] = np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 50)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score 75th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'], 75), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'ES Score Max'] = metrics.loc[metrics['Year Ending'] == year, 'ENERGY STAR Score'].max()
        
        # Source EUI Distribution Columns
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Min'] = metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'].min()
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI 25th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 25), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Median'] = np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 50)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI 75th Percentile'] = round(np.nanpercentile(metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'], 75), 2)
        portfolio_metrics.loc[portfolio_metrics['Year Ending'] == year, 'Weather Normalized Source EUI Max'] = metrics.loc[metrics['Year Ending'] == year, 'Weather Normalized Source EUI (kBtu/ft²)'].max()

    # Format the portfolio_metrics dataframe
    int_cols = ['ES Score Min', 'ES Score 25th Percentile', 'ES Score Median', 
                'ES Score 75th Percentile', 'ES Score Max']

    for col in int_cols: 
        portfolio_metrics[col] = portfolio_metrics[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
    portfolio_metrics.replace('nan', np.nan, inplace = True)

    return portfolio_metrics

# Create a function that will return a processed workbook to download
def create_workbook(portfolio_metrics, portfolio_df, compliance_data_21, best_eui_shifts, worst_eui_shifts):
    data = BytesIO()
    with pd.ExcelWriter(data) as writer:
        portfolio_metrics.to_excel(writer, sheet_name = 'Portfolio Distribution', index = False)
        portfolio_df.to_excel(writer, sheet_name = 'Portfolio Metrics', index = False)
        compliance_data_21.to_excel(writer, sheet_name = '2022 EBEWE Compliance', index = False)
        best_eui_shifts.to_excel(writer, sheet_name = 'Best EUI Shifts', index = False)
        worst_eui_shifts.to_excel(writer, sheet_name = 'Worst EUI Shifts', index = False)
    
    workbook = data.getvalue()
    return workbook