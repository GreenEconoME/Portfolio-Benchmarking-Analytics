import pandas as pd
import numpy as np
import streamlit as st

# Defining a helper function to find the min of a list of tuples based on first element of tuple, and return the second value of tuple
def filter_tuple_list(given_list, target_value):
    for x, y in given_list:
        if x == target_value:
            return y

# Create the 2022 compliance year EBEWE data
def create_compliance(metrics, comp_period):

    # Create a variable to hold the comparative period from the dropdown
    comparative_period = comp_period
    
    # Create a dict that has the comparative periods as keys, 
    # And the associated numbers to classify the EBEWE compliance date by LA building ID, as well as the starting year of the compliance period
    comp_dict = {'Dec 1, 2021: Comparative Period Jan 2016 - Dec 2020': [['0', '1'], 2016], 
                'Dec 1, 2022: Comparative Period Jan 2017 - Dec 2021': [['2', '3'], 2017], 
                'Dec 1, 2023: Comparative Period Jan 2018 - Dec 2022': [['4', '5'], 2018], 
                'Dec 1, 2024: Comparative Period Jan 2019 - Dec 2023': [['6', '7'], 2019], 
                'Dec 1, 2025: Comparative Period Jan 2020 - Dec 2024': [['8', '9'], 2020]}

    # Getting the rows that contain properties that need to comply during chosen comparative period
    compliance = []
    for row in metrics.index:
        if not pd.isnull(metrics.loc[row, 'Los Angeles Building ID']):
            if metrics.loc[row, 'Los Angeles Building ID'][-1] in comp_dict[comparative_period][0]:
                compliance.append(row)


    # Creating a dataframe to hold the EBEWE data for buildings within chosen compliance year
    data = []
    for prop in metrics.loc[compliance, 'Property Name'].unique():
        # Create and populate a dictionary to hold each properties information
        prop_info = {}
        prop_info['ESPM Property Id'] = metrics.loc[metrics['Property Name'] == prop, 'Property Id'].values[0]
        prop_info['Property Name'] = prop
        prop_info['LA Building Id'] = metrics.loc[metrics['Property Name'] == prop, 'Los Angeles Building ID'].values[0]
        prop_info['Square Footage'] = metrics.loc[metrics['Property Name'] == prop, 'Property GFA - Self-Reported (ft²)'].values[0]
        prop_info['Primary Property Type'] = metrics.loc[metrics['Property Name'] == prop, 'Primary Property Type - Self Selected'].values[0]

        # Append the property information dictionary to the list of data
        data.append(prop_info)
        
    # Create a dataframe from each properties information
    compliance_data = pd.DataFrame(data)
   
    # Check if df is empty - will happen if no buildings have an LA Building ID
    if not compliance_data.empty:
        
        # Populating the EBEWE Compliance comparative period data   
        for row in compliance_data.index:
            for year in range(comp_dict[comparative_period][1], comp_dict[comparative_period][1] + 5):
                if not metrics.loc[metrics['Year Ending'] == f'{year}-12-31'].empty:
                    # Populate the comparative period's Energy Star Score
                        compliance_data.loc[row, f'{year} ES Score'] = metrics.loc[(metrics['Property Id'] == compliance_data.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'ENERGY STAR Score'].item()
                        
                    # Populate the comparative period's Source EUI
                        compliance_data.loc[row, f'{year} Weather Normalized Source EUI'] = metrics.loc[(metrics['Property Id'] == compliance_data.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Weather Normalized Source EUI (kBtu/ft²)'].item()
                        
                    # Populate the comparative period's Water UI
                        compliance_data.loc[row, f'{year} Water UI'] = metrics.loc[(metrics['Property Id'] == compliance_data.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{year}-12-31'), 'Water Use Intensity (All Water Sources) (gal/ft²)'].item()
                
                else:
                    compliance_data.loc[row, f'{year} ES Score'] = np.nan
                    compliance_data.loc[row, f'{year} Weather Normalized Source EUI'] = np.nan
                    compliance_data.loc[row, f'{year} Water UI'] = np.nan
            # Populate the National Median Source EUI column for the last year in the compliance period
            if not metrics.loc[metrics['Year Ending'] == f'{comp_dict[comparative_period][1] + 4}-12-31'].empty:
                compliance_data.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI'] = metrics.loc[(metrics['Property Id'] == compliance_data.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == f'{comp_dict[comparative_period][1] + 4}-12-31'), 'National Median Source EUI (kBtu/ft²)'].item()
            else:
                compliance_data.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI'] = np.nan
            # Populate the comparative period's Best Source EUI % Change
            # Create a list to hold the percent changes for each year
            eui_percent_changes = []
            for year in range(comp_dict[comparative_period][1], comp_dict[comparative_period][1] + 5):
                if pd.notnull(compliance_data.loc[row, f'{year} Weather Normalized Source EUI']):
                    eui_percent_changes.append(((compliance_data.loc[row, f'{comp_dict[comparative_period][1] + 4} Weather Normalized Source EUI'] - compliance_data.loc[row, f'{year} Weather Normalized Source EUI']) / compliance_data.loc[row, f'{year} Weather Normalized Source EUI'], year))
            # Set the Best EUI % Reduction value to the best percent change
            if len(eui_percent_changes) != 0:
                compliance_data.loc[row, 'Best EUI % Reduction'] = round(min(eui_percent_changes, key = lambda x: x[0])[0] * 100, 2)
                # Populate the Comparative Year of Best Source EUI % Change
                compliance_data.loc[row, 'Best EUI % Reduction Year'] = filter_tuple_list(eui_percent_changes, min(eui_percent_changes, key = lambda x: x[0])[0])
            
            # Populate the Energy Exemption #1 column
            if compliance_data.loc[row, f'{comp_dict[comparative_period][1] + 4} ES Score'] >= 75:
                compliance_data.loc[row, 'Energy Exemption #1?'] = 'Possible'
            else:
                compliance_data.loc[row, 'Energy Exemption #1?'] = 'No'        
            
            # Populate the Energy Exemption #4 column
            if compliance_data.loc[row, 'Best EUI % Reduction'] <= -15: 
                compliance_data.loc[row, 'Energy Exemption #4?'] = 'Yes'
            else:
                compliance_data.loc[row, 'Energy Exemption #4?'] = 'No'
                
            # Populate the comparative period's Best Water UI % Change
            # Create a list to hold the percent changes for each year
            wui_percent_changes = []
            for year in range(comp_dict[comparative_period][1], comp_dict[comparative_period][1] + 5):
                if pd.notnull(compliance_data.loc[row, f'{year} Water UI']):
                    wui_percent_changes.append(((compliance_data.loc[row, f'{comp_dict[comparative_period][1] + 4} Water UI'] - compliance_data.loc[row, f'{year} Water UI']) / compliance_data.loc[row, f'{year} Water UI'], year))
            # Set the Best Water UI % Reduction value to the best percent change
            if len(wui_percent_changes) != 0:
                compliance_data.loc[row, 'Best Water UI % Change'] = round(min(wui_percent_changes, key = lambda x: x[0])[0] * 100, 2)
                # Populate the Best Water UI % Reduction Year column
                compliance_data.loc[row, 'Best Water UI % Change Year'] = filter_tuple_list(wui_percent_changes, min(wui_percent_changes, key = lambda x: x[0])[0])
            
            # Populate the Water Exemption #1 column
            if compliance_data.loc[row, 'Best Water UI % Change'] <= -20:
                compliance_data.loc[row, 'Water Exemption #1?'] = 'Yes'
            else:
                compliance_data.loc[row, 'Water Exemption #1?'] = 'No'

        # Format the compliance_data columns that are integers
        int_cols = ['Square Footage', 
                    f'{comp_dict[comparative_period][1]} ES Score', 
                    f'{comp_dict[comparative_period][1] + 1} ES Score', 
                    f'{comp_dict[comparative_period][1] + 2} ES Score', 
                    f'{comp_dict[comparative_period][1] + 3} ES Score', 
                    f'{comp_dict[comparative_period][1] + 4} ES Score', 
                    'Best EUI % Reduction Year', 
                    'Best Water UI % Change Year']
        for col in int_cols: 
            compliance_data[col] = compliance_data[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
        # Replace the nan strings with actual nans   
        compliance_data.replace('nan', np.nan, inplace = True)

        # Reindex the columns
        compliance_data = compliance_data.reindex(columns = ['ESPM Property Id',
                                                            'Property Name',
                                                            'LA Building Id',
                                                            'Square Footage',
                                                            f'{comp_dict[comparative_period][1]} ES Score',
                                                            f'{comp_dict[comparative_period][1] + 1} ES Score',
                                                            f'{comp_dict[comparative_period][1] + 2} ES Score',
                                                            f'{comp_dict[comparative_period][1] + 3} ES Score',
                                                            f'{comp_dict[comparative_period][1] + 4} ES Score',
                                                            f'{comp_dict[comparative_period][1]} Weather Normalized Source EUI',
                                                            f'{comp_dict[comparative_period][1] + 1} Weather Normalized Source EUI',
                                                            f'{comp_dict[comparative_period][1] + 2} Weather Normalized Source EUI',
                                                            f'{comp_dict[comparative_period][1] + 3} Weather Normalized Source EUI',
                                                            f'{comp_dict[comparative_period][1] + 4} Weather Normalized Source EUI',
                                                            f'{comp_dict[comparative_period][1]} Water UI',
                                                            f'{comp_dict[comparative_period][1] + 1} Water UI',
                                                            f'{comp_dict[comparative_period][1] + 2} Water UI',
                                                            f'{comp_dict[comparative_period][1] + 3} Water UI',
                                                            f'{comp_dict[comparative_period][1] + 4} Water UI',
                                                            f'{comp_dict[comparative_period][1] + 4} National Median Source EUI',
                                                            'Best EUI % Reduction',
                                                            'Best EUI % Reduction Year',
                                                            'Energy Exemption #1?',
                                                            'Energy Exemption #4?',
                                                            'Best Water UI % Change',
                                                            'Best Water UI % Change Year',
                                                            'Water Exemption #1?'])

    # Remove the empty columns
    for col in compliance_data.columns:
        if compliance_data[col].isnull().all():
            compliance_data.drop(columns = [col], inplace = True)

    return compliance_data