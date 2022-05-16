import pandas as pd
import numpy as np

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