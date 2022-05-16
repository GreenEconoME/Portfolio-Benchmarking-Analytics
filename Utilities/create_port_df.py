import pandas as pd
import numpy as np

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