import pandas as pd
import numpy as np

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