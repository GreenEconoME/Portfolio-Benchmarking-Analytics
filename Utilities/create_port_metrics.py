import pandas as pd
import numpy as np

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