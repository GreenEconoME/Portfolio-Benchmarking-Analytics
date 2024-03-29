import pandas as pd
import numpy as np

# Create a function to make the top quartile for Source EUI Change
def top_quartile_SEUI(portfolio_df, comp_period):

    # Create a variable to hold the comparative period from the dropdown
    comparative_period = comp_period

    # Create a dict that has the comparative periods as keys, 
    # And the associated numbers to classify the EBEWE compliance date by LA building ID, as well as the starting year of the compliance period
    comp_dict = {'Dec 1, 2021: Comparative Period 2016 - 2020': [['0', '1'], 2016], 
                'Dec 1, 2022: Comparative Period 2017 - 2021': [['2', '3'], 2017], 
                'Dec 1, 2023: Comparative Period 2018 - 2022': [['4', '5'], 2018], 
                'Dec 1, 2024: Comparative Period 2019 - 2023': [['6', '7'], 2019], 
                'Dec 1, 2025: Comparative Period 2020 - 2024': [['8', '9'], 2020]}

    best_eui_shifts = portfolio_df.loc[(portfolio_df[f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} EUI % Change'] <= 
                                        np.nanpercentile(portfolio_df[f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} EUI % Change'], 
                                        25))]
    best_eui_shifts.sort_values(by = f'{comp_dict[comparative_period][1] + 3}-{comp_dict[comparative_period][1] + 4} EUI % Change', 
                                inplace = True)

    # Format the best_eui_shifts dataframe
    int_cols = ['Square Footage', 
                f'{comp_dict[comparative_period][1] + 2} ES Score', 
                f'{comp_dict[comparative_period][1] + 3} ES Score', 
                f'{comp_dict[comparative_period][1] + 4} ES Score']

    # Remove the .0 from the integer column values for exporting to excel
    for col in int_cols: 
        best_eui_shifts[col] = best_eui_shifts[col].astype(str).apply(lambda x: x.replace('.0', '')) 
        
    # Replace the string nans with numpy NaNs
    best_eui_shifts.replace('nan', np.nan, inplace = True)

    return best_eui_shifts