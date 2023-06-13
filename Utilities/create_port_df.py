# Import dependencies
import pandas as pd
import numpy as np
import streamlit as st

# Create function to make benchmarking metrics for full portfolio
def create_port_df(metrics, comp_period):
    # Create a variable to hold the comparative period from the dropdown
    comparative_period = comp_period
    
    # Create a dict that has the comparative periods as keys, 
    # And the associated numbers to classify the EBEWE compliance date by LA building ID, as well as the starting year of the compliance period
    comp_dict = {'Dec 1, 2021: Comparative Period 2016 - 2020': [['0', '1'], 2016], 
                'Dec 1, 2022: Comparative Period 2017 - 2021': [['2', '3'], 2017], 
                'Dec 1, 2023: Comparative Period 2018 - 2022': [['4', '5'], 2018], 
                'Dec 1, 2024: Comparative Period 2019 - 2023': [['6', '7'], 2019], 
                'Dec 1, 2025: Comparative Period 2020 - 2024': [['8', '9'], 2020]}

    # Creating a dataframe to hold the portfolio data for buildings
    data = []
    for prop in metrics['Property Name'].unique():
        # Create and populate a dictionary to hold each properties information
        prop_info = {}
        prop_info['ESPM Property Id'] = metrics.loc[metrics['Property Name'] == prop, 'Portfolio Manager Property ID'].values[0]
        prop_info['Property Name'] = prop
        prop_info['LA Building Id'] = metrics.loc[metrics['Property Name'] == prop, 'Los Angeles Building ID'].values[0]
        prop_info['Square Footage'] = metrics.loc[metrics['Property Name'] == prop, 'Property GFA - Self-Reported (ft²)'].values[0]
        prop_info['Primary Property Type'] = metrics.loc[metrics['Property Name'] == prop, 'Primary Property Type - Self Selected'].values[0]

        # Append the property information dictionary to the list of data
        data.append(prop_info)
        
    # Create a dataframe from each properties information
    portfolio_df = pd.DataFrame(data)

    # Take note of the active month and day that the espm report was created for
    active_month = metrics['Year Ending'].dt.month.unique()[0]
    active_day = metrics['Year Ending'].dt.day.unique()[0]
    # Populating the EBEWE Compliance comparative period data
    for row in portfolio_df.index:
        
        # Populate the last three years Energy Star Score, Source EUI and Water UI
        for year in range(comp_dict[comparative_period][1] + 2, comp_dict[comparative_period][1] + 5):
            year_ending = pd.to_datetime(f"{year}-{active_month}-{active_day}").strftime("%Y-%m-%d")

            if not metrics.loc[metrics['Year Ending'] == year_ending].empty:
                portfolio_df.loc[row, f'{year} ES Score'] = metrics.loc[(metrics['Portfolio Manager Property ID'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == year_ending), 'ENERGY STAR Score'].item()
                
                # Populate the last three years Source EUI
                portfolio_df.loc[row, f'{year} Weather Normalized Source EUI'] = metrics.loc[(metrics['Portfolio Manager Property ID'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == year_ending), 'Weather Normalized Source EUI (kBtu/ft²)'].item()
                
                # Populate the last three years Water UI
                portfolio_df.loc[row, f'{year} Water UI'] = metrics.loc[(metrics['Portfolio Manager Property ID'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == year_ending), 'Water Use Intensity (All Water Sources) (gal/ft²)'].item()
            else:
                portfolio_df.loc[row, f'{year} ES Score'] = np.nan
                portfolio_df.loc[row, f'{year} Weather Normalized Source EUI'] = np.nan
                portfolio_df.loc[row, f'{year} Water UI'] = np.nan
        # Populate the GHG Emissions Intensity, National Median Source EUI, % difference from National Source EUI, Source EUI % Change, Water UI % Change
        # for the last year(s) of the comparative period
        if not metrics.loc[metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 4}-{active_month}-{active_day}').strftime("%Y-%m-%d")].empty:
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} Total GHG Emissions Intensity (kgCO2e/ft²)'] = metrics.loc[(metrics['Portfolio Manager Property ID'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 4}-{active_month}-{active_day}').strftime("%Y-%m-%d")), 'Total (Location-Based) GHG Emissions Intensity (kgCO2e/ft²)'].item()
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI'] = metrics.loc[(metrics['Portfolio Manager Property ID'] == portfolio_df.loc[row, 'ESPM Property Id']) & (metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 4}-{active_month}-{active_day}').strftime("%Y-%m-%d")), 'National Median Source EUI (kBtu/ft²)'].item()
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} % Difference From National Source EUI'] = round(((portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} Weather Normalized Source EUI'] - portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI']) / portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI']) * 100, 2)
                

                
        else:
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} Total GHG Emissions Intensity (kgCO2e/ft²)'] = np.nan
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} National Median Source EUI'] = np.nan
            portfolio_df.loc[row, f'{comp_dict[comparative_period][1] + 4} % Difference From National Source EUI'] = np.nan
            
    # Create helper function to make a percent change column
    def pct_change(df, new_col, old_col):
        return round(((df[new_col] - df[old_col]) / df[old_col]) * 100, 2)

    # Populate the Source EUI % Change, ES Score % Change and Water UI % Change for the last two years of the comparative period
    if not metrics.loc[metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 3}-{active_month}-{active_day}').strftime("%Y-%m-%d")].empty:
        if not metrics.loc[metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 4}-{active_month}-{active_day}').strftime("%Y-%m-%d")].empty:
            portfolio_df[f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} EUI % Change'] = pct_change(portfolio_df, 
                                                                                                                                         f'{comp_dict[comparative_period][1] + 4} Weather Normalized Source EUI',
                                                                                                                                         f'{comp_dict[comparative_period][1] + 3} Weather Normalized Source EUI')
            portfolio_df[f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} Water UI % Change'] = pct_change(portfolio_df, 
                                                                                                                                         f'{comp_dict[comparative_period][1] + 4} Water UI',
                                                                                                                                         f'{comp_dict[comparative_period][1] + 3} Water UI')
            portfolio_df[f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} ES Score % Change'] = pct_change(portfolio_df, 
                                                                                                                                         f'{comp_dict[comparative_period][1] + 4} ES Score',
                                                                                                                                         f'{comp_dict[comparative_period][1] + 3} ES Score')


        # Populate the Source EUI % Change, ES Score % Change and Water UI % Change for the third and fourth years of the comparative period
        if not metrics.loc[metrics['Year Ending'] == pd.to_datetime(f'{comp_dict[comparative_period][1] + 2}-{active_month}-{active_day}').strftime("%Y-%m-%d")].empty:
            portfolio_df[f'{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} EUI % Change'] = pct_change(portfolio_df, 
                                                                                                                             f'{comp_dict[comparative_period][1] + 3} Weather Normalized Source EUI',
                                                                                                                             f'{comp_dict[comparative_period][1] + 2} Weather Normalized Source EUI')
            portfolio_df[f'{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} Water UI % Change'] = pct_change(portfolio_df, 
                                                                                                                             f'{comp_dict[comparative_period][1] + 3} Water UI',
                                                                                                                             f'{comp_dict[comparative_period][1] + 2} Water UI')
            portfolio_df[f'{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} ES Score % Change'] = pct_change(portfolio_df, 
                                                                                                                             f'{comp_dict[comparative_period][1] + 3} ES Score',
                                                                                                                             f'{comp_dict[comparative_period][1] + 2} ES Score')
    # Format the portfolio_df dataframe
    int_cols = ['Square Footage', 
                f'{comp_dict[comparative_period][1] + 2} ES Score', 
                f'{comp_dict[comparative_period][1] + 3} ES Score', 
                f'{comp_dict[comparative_period][1] + 4} ES Score']

    for col in int_cols: 
        portfolio_df[col] = portfolio_df[col].astype(str).apply(lambda x: x.replace('.0', '')) 

    # Replace with string nan values with actual NaNs 
    portfolio_df.replace('nan', np.nan, inplace = True)
    
    # Reindex the columns
    portfolio_df = portfolio_df.reindex(columns = ["ESPM Property Id",
                                                    "Property Name",
                                                    "LA Building Id",
                                                    "Square Footage",
                                                    "Primary Property Type",
                                                    f'{comp_dict[comparative_period][1] + 2} ES Score', 
                                                    f'{comp_dict[comparative_period][1] + 3} ES Score', 
                                                    f'{comp_dict[comparative_period][1] + 4} ES Score',
                                                    f"{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} ES Score % Change",
                                                    f"{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} ES Score % Change",
                                                    f"{comp_dict[comparative_period][1] + 2} Weather Normalized Source EUI",
                                                    f"{comp_dict[comparative_period][1] + 3} Weather Normalized Source EUI",
                                                    f"{comp_dict[comparative_period][1] + 4} Weather Normalized Source EUI",
                                                    f"{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} EUI % Change",
                                                    f"{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} EUI % Change",
                                                    f"{comp_dict[comparative_period][1] + 4} National Median Source EUI",
                                                    f"{comp_dict[comparative_period][1] + 4} % Difference From National Source EUI",
                                                    f"{comp_dict[comparative_period][1] + 2} Water UI",
                                                    f"{comp_dict[comparative_period][1] + 3} Water UI",
                                                    f"{comp_dict[comparative_period][1] + 4} Water UI",
                                                    f"{comp_dict[comparative_period][1] + 2}-{comp_dict[comparative_period][1] + 3} Water UI % Change",
                                                    f"{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} Water UI % Change",
                                                    f"{comp_dict[comparative_period][1] + 4} Total GHG Emissions Intensity (kgCO2e/ft²)"])


    return portfolio_df