# Import dependencies
import pandas as pd
import numpy as np

# Create function to clean initial ESPM export
def clean_metrics(metrics):

    # Remove parent columns - contain no data but come with download
    metrics.drop(columns = ['Parent Property Id', 'Parent Property Name'], inplace = True)

    # Replace Not Available with NaN values, remove leading and trailing zeros from building ID
    metrics.replace('Not Available', np.nan, inplace = True)

    # Remove any leading or trailing spaces within the LA building ids
    metrics['Los Angeles Building ID'] = metrics['Los Angeles Building ID'].astype(str).str.strip()

    return metrics