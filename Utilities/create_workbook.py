# Import dependencies
import pandas as pd
from io import BytesIO

# Create a function that will return a processed workbook to download
def create_workbook(portfolio_metrics, portfolio_df, compliance_data, best_eui_shifts, worst_eui_shifts, comp_period):

    # Create a variable to hold the comparative period from the dropdown
    comparative_period = comp_period

    # Create a dict that has the comparative periods as keys, 
    # And the associated numbers to classify the EBEWE compliance date by LA building ID, as well as the starting year of the compliance period
    comp_dict = {'Dec 1, 2021: Comparative Period Jan 2016 - Dec 2020': [['0', '1'], 2016], 
                'Dec 1, 2022: Comparative Period Jan 2017 - Dec 2021': [['2', '3'], 2017], 
                'Dec 1, 2023: Comparative Period Jan 2018 - Dec 2022': [['4', '5'], 2018], 
                'Dec 1, 2024: Comparative Period Jan 2019 - Dec 2023': [['6', '7'], 2019], 
                'Dec 1, 2025: Comparative Period Jan 2020 - Dec 2024': [['8', '9'], 2020]}

    # Create the object to hold the excel workbook export and populate the worksheets with the generated dataframes
    data = BytesIO()
    with pd.ExcelWriter(data) as writer:
        portfolio_metrics.to_excel(writer, sheet_name = 'Portfolio Distribution', index = False)
        portfolio_df.to_excel(writer, sheet_name = 'Portfolio Metrics', index = False)
        compliance_data.to_excel(writer, sheet_name = f'{comp_dict[comparative_period][1] + 5} EBEWE Compliance', index = False)
        best_eui_shifts.to_excel(writer, sheet_name = 'Best EUI Shifts', index = False)
        worst_eui_shifts.to_excel(writer, sheet_name = 'Worst EUI Shifts', index = False)
    
    workbook = data.getvalue()
    
    return workbook