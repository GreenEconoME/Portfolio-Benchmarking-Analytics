import pandas as pd
import numpy as np

# Defining a helper function to find the min of a list of tuples based on first element of tuple, and return the second value of tuple
def filter_tuple_list(given_list, target_value):
    for x, y in given_list:
        if x == target_value:
            return y

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