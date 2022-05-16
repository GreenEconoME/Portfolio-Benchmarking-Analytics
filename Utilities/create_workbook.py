import pandas as pd
from io import BytesIO

# Create a function that will return a processed workbook to download
def create_workbook(portfolio_metrics, portfolio_df, compliance_data_21, best_eui_shifts, worst_eui_shifts):
    data = BytesIO()
    with pd.ExcelWriter(data) as writer:
        portfolio_metrics.to_excel(writer, sheet_name = 'Portfolio Distribution', index = False)
        portfolio_df.to_excel(writer, sheet_name = 'Portfolio Metrics', index = False)
        compliance_data_21.to_excel(writer, sheet_name = '2022 EBEWE Compliance', index = False)
        best_eui_shifts.to_excel(writer, sheet_name = 'Best EUI Shifts', index = False)
        worst_eui_shifts.to_excel(writer, sheet_name = 'Worst EUI Shifts', index = False)
    
    workbook = data.getvalue()
    return workbook